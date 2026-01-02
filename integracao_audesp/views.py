# SysGov_Project/integracao_audesp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.conf import settings
import json

# Importamos o nosso novo "carteiro"
from . import services

# Importações de Modelos
from .models import AudespConfiguracao, SubmissaoAudesp
from contratacoes.models import ETP, Contrato, AtaRegistroPrecos
from licitacoes.models import Edital
from financeiro.models import DocumentoFiscal, Pagamento

# --- LÓGICA PRINCIPAL DO PAINEL DE SUBMISSÃO ---

@login_required
def painel_audesp_view(request):
    """
    Exibe os documentos pendentes e processa o envio para a API do TCE.
    """
    # --- LÓGICA DE POST (ENVIO PARA O TCE) ---
    if request.method == 'POST' and 'enviar_para_tce' in request.POST:
        doc_type = request.POST.get('doc_type')
        doc_id = request.POST.get('doc_id')
        json_content = None
        documento_obj = None

        # 1. Gera o JSON correto dependendo do tipo de documento
        if doc_type == 'contrato':
            documento_obj = get_object_or_404(Contrato, pk=doc_id)
            json_response = gerar_contrato_audesp_json(request, documento_obj.pk)
            json_content = json_response.content
        elif doc_type == 'edital':
            documento_obj = get_object_or_404(Edital, pk=doc_id)
            json_response = gerar_edital_audesp_json(request, documento_obj.pk)
            json_content = json_response.content
        
        if json_content and documento_obj:
            # 2. Busca as credenciais (que estarão no seu .env ou nas configurações do servidor)
            API_KEY_TCE = getattr(settings, 'API_KEY_TCE', 'SUA_CHAVE_DE_TESTE_AQUI')
            URL_HOMOLOGACAO_TCE = getattr(settings, 'URL_HOMOLOGACAO_TCE', 'URL_DE_TESTE_FORNECIDA_PELO_TCE')

            # 3. Chama o nosso "carteiro" para fazer o envio
            resultado_envio = services.enviar_pacote_audesp(json.loads(json_content), API_KEY_TCE, URL_HOMOLOGACAO_TCE)
            
            # 4. Regista o resultado no nosso histórico
            submissao = SubmissaoAudesp.objects.create(
                documento_submetido=documento_obj,
                usuario_responsavel=request.user,
                status_tce='ENVIADO' if resultado_envio['sucesso'] else 'ERRO_ENVIO',
                resposta_tce=str(resultado_envio.get('resposta') or resultado_envio.get('erro')),
                protocolo_tce=resultado_envio.get('resposta', {}).get('protocolo')
            )

            if resultado_envio['sucesso']:
                messages.success(request, f"Documento enviado com sucesso! Protocolo TCE: {submissao.protocolo_tce}")
            else:
                messages.error(request, f"Falha no envio para o TCE: {resultado_envio.get('erro')}")

        return redirect('integracao_audesp:painel_audesp')

    # --- LÓGICA DE GET (Exibição da página) ---
    etp_content_type = ContentType.objects.get_for_model(ETP)
    etps_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=etp_content_type, status_tce='ACEITO').values_list('object_id', flat=True)
    etps_pendentes = ETP.objects.filter(status='APROVADO').exclude(pk__in=etps_submetidos_ids)
    
    edital_content_type = ContentType.objects.get_for_model(Edital)
    editais_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=edital_content_type, status_tce='ACEITO').values_list('object_id', flat=True)
    editais_pendentes = Edital.objects.filter(status__in=['PUBLICADO', 'HOMOLOGADO']).exclude(pk__in=editais_submetidos_ids)

    contrato_content_type = ContentType.objects.get_for_model(Contrato)
    contratos_submetidos_ids = SubmissaoAudesp.objects.filter(content_type=contrato_content_type, status_tce='ACEITO').values_list('object_id', flat=True)
    contratos_pendentes = Contrato.objects.filter(status='VIGENTE').exclude(pk__in=contratos_submetidos_ids)
    
    context = {
        'etps_pendentes': etps_pendentes,
        'editais_pendentes': editais_pendentes,
        'contratos_pendentes': contratos_pendentes,
        'titulo_pagina': 'Painel de Submissão AUDESP'
    }
    return render(request, 'integracao_audesp/painel_audesp.html', context)


@login_required
def listar_submissoes_audesp(request):
    """ Exibe o histórico de todas as submissões geradas. """
    submissoes = SubmissaoAudesp.objects.all().order_by('-data_submissao')
    context = {'submissoes': submissoes, 'titulo_pagina': 'Histórico de Submissões AUDESP'}
    return render(request, 'integracao_audesp/listar_submissoes.html', context)


# --- VIEWS DE GERAÇÃO DE JSON ---

def get_audesp_config_data():
    """ Função auxiliar para buscar os dados de configuração. """
    try:
        config = AudespConfiguracao.objects.first()
        if config:
            return {"municipio_codigo": config.municipio_codigo_audesp, "entidade_codigo": config.entidade_codigo_audesp}
    except AudespConfiguracao.DoesNotExist:
        pass
    return {"municipio_codigo": "00000", "entidade_codigo": "00000"}

@login_required
def gerar_etp_audesp_json(request, etp_id):
    etp = get_object_or_404(ETP, pk=etp_id)
    config_data = get_audesp_config_data()
    etp_json_data = {
        "municipioCodigo": config_data.get("municipio_codigo"),
        "entidadeCodigo": config_data.get("entidade_codigo"),
        "identificadorDocumento": etp.numero_processo,
        "titulo": etp.titulo,
        "valorEstimado": float(etp.estimativa_valor),
        "status": etp.status
    }
    return JsonResponse(etp_json_data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})

@login_required
def gerar_edital_audesp_json(request, edital_id):
    edital = get_object_or_404(Edital, pk=edital_id)
    config_data = get_audesp_config_data()
    edital_json_data = {
        "Descritor": {"AnoExercicio": edital.data_publicacao.year, "TipoDocumento": "EDITAL"},
        "Edital": {"NumeroEdital": edital.numero_edital, "ObjetoLicitacao": edital.titulo}
    }
    return JsonResponse(edital_json_data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})

@login_required
def gerar_contrato_audesp_json(request, contrato_id):
    contrato = get_object_or_404(Contrato, pk=contrato_id)
    config_data = get_audesp_config_data()
    dados_json = {
        "descritor": {"municipio": config_data.get("municipio_codigo"), "codigoContrato": f"{contrato.numero_contrato}/{contrato.ano_contrato}"},
        "objetoContrato": contrato.objeto,
        "valorGlobal": float(contrato.valor_total),
        "dataAssinatura": contrato.data_assinatura.strftime("%Y-%m-%d"),
        "niFornecedor": contrato.contratado.cnpj.replace('.', '').replace('/', '').replace('-', ''),
        "nomeRazaoSocialFornecedor": contrato.contratado.razao_social,
    }
    return JsonResponse(dados_json, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})