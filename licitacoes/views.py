# SysGov_Project/licitacoes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.forms import inlineformset_factory # Para formsets
from django.db import transaction, IntegrityError # Para transações atômicas
from django.db.models import Q # Para queries complexas (se for usar)
from django.utils import timezone # Para campos de data/hora
from .models import (
    Edital, Lance, Lote, ItemLicitado, ResultadoLicitacao,Pregao, ParticipanteLicitacao,
    STATUS_EDITAL_CHOICES,
    TIPO_INSTRUMENTO_CONVOCATORIO_CHOICES, MODALIDADE_LICITACAO_CHOICES, MODO_DISPUTA_CHOICES,
    VEICULO_PUBLICACAO_CHOICES, TIPO_BENEFICIO_CHOICES, CRITERIO_JULGAMENTO_CHOICES, ITEM_CATEGORIA_CHOICES, Pregao
)

from .forms import (
    EditalForm, LoteForm, ItemLicitadoForm, ResultadoLicitacaoForm,ParticipanteForm, LanceForm
    )

from core.models import Processo
LoteFormSet = inlineformset_factory(Edital, Lote, form=LoteForm, extra=1, can_delete=True)
ItemLicitadoFormSet = inlineformset_factory(Edital, ItemLicitado, form=ItemLicitadoForm, extra=1, can_delete=True)
# Se você tiver itens dentro de lotes, precisaria de um formset aninhado ou outra abordagem


# --- VIEWS PARA EDITAL ---

@login_required
def listar_editais(request):
    # Otimização: .select_related() busca os dados dos modelos
    # relacionados (com ForeignKey) em uma única query SQL.
    editais = Edital.objects.select_related(
        'processo_vinculado', 'responsavel_publicacao'
    ).all().order_by('-data_publicacao')

    context = {
        'editais': editais,
        'titulo_pagina': 'Lista de Editais de Licitação',
    }
    return render(request, 'licitacoes/listar_editais.html', context)

@login_required
def criar_edital(request, processo_id=None):
    processo_core = None
    if processo_id:
        processo_core = get_object_or_404(Processo, id=processo_id)
        # Opcional: Se já existe um Edital vinculado a este Processo, redirecione para editá-lo
        if hasattr(processo_core, 'edital_licitacao'):
            messages.info(request, "Este processo já possui um Edital. Você será redirecionado para editá-lo.")
            return redirect('licitacoes:editar_edital', pk=processo_core.edital_licitacao.pk)

    if request.method == 'POST':
        form = EditalForm(request.POST) # Usando o EditalForm original
        # Se você quiser usar os novos forms do AUDESP, mude para EditalLicitacaoForm
        # form = EditalLicitacaoForm(request.POST)

        lotes_formset = LoteFormSet(request.POST, prefix='lotes')
        itens_formset = ItemLicitadoFormSet(request.POST, prefix='itens')

        if form.is_valid() and lotes_formset.is_valid() and itens_formset.is_valid():
            try:
                with transaction.atomic():
                    edital = form.save(commit=False)
                    edital.responsavel_publicacao = request.user
                    if processo_core:
                        edital.processo_vinculado = processo_core
                    edital.save()

                    lotes_formset.instance = edital
                    lotes_formset.save()

                    itens_formset.instance = edital
                    itens_formset.save()

                messages.success(request, 'Edital criado com sucesso!')
                if processo_core:
                    return redirect('detalhes_processo', processo_id=processo_core.id)
                else:
                    return redirect('licitacoes:detalhar_edital', pk=edital.pk)

            except Exception as e:
                messages.error(request, f"Não foi possível salvar o Edital devido a um erro inesperado: {e}")
                print(f"Erro no salvamento do Edital (bloco try/except): {e}")
        else:
            messages.error(request, 'Erro ao criar Edital. Verifique os campos.')
            print("====================================")
            print("ERRO DE VALIDAÇÃO DO FORMULÁRIO EDITAL:")
            print("Erros do formulário principal (Edital):", form.errors)
            print("Erros não-campo do formulário principal (Edital):", form.non_field_errors)
            print("Erros do formset de Lotes:", lotes_formset.errors)
            print("Erros do formset de Itens:", itens_formset.errors)
            print("====================================")
    else: # GET request
        initial_data = {}
        if processo_core:
            initial_data['numero_processo_origem'] = processo_core.numero_protocolo

        form = EditalForm(initial=initial_data) # Usando o EditalForm original
        # Se você quiser usar os novos forms do AUDESP, mude para EditalLicitacaoForm
        # form = EditalLicitacaoForm(initial=initial_data)

        lotes_formset = LoteFormSet(prefix='lotes')
        itens_formset = ItemLicitadoFormSet(prefix='itens')

    context = {
        'form': form,
        'lotes_formset': lotes_formset,
        'itens_formset': itens_formset,
        'processo_core': processo_core,
        'titulo_pagina': f'Criar Edital para Processo: {processo_core.titulo}' if processo_core else 'Criar Novo Edital'
    }
    return render(request, 'licitacoes/criar_edital.html', context)


@login_required
def editar_edital(request, pk):
    edital = get_object_or_404(Edital, pk=pk)

    if request.method == 'POST':
        # MUDANÇA 1: Adicionado request.FILES para lidar com o upload do PDF
        form = EditalForm(request.POST, request.FILES, instance=edital)
        
        lotes_formset = LoteFormSet(request.POST, instance=edital, prefix='lotes')
        itens_formset = ItemLicitadoFormSet(request.POST, instance=edital, prefix='itens')

        if form.is_valid() and lotes_formset.is_valid() and itens_formset.is_valid():
            try:
                with transaction.atomic():
                    # MUDANÇA 2: Usando o padrão commit=False para salvamento seguro
                    
                    # Salva o formulário principal primeiro para garantir que o objeto 'edital' exista
                    saved_edital = form.save()

                    # Associa os formsets à instância salva do edital
                    lotes_formset.instance = saved_edital
                    itens_formset.instance = saved_edital

                    # Agora salva os formsets
                    lotes_formset.save()
                    itens_formset.save()
                    
                messages.success(request, 'Edital atualizado com sucesso!')
                return redirect('licitacoes:detalhar_edital', pk=edital.pk)
            except Exception as e:
                messages.error(request, f"Não foi possível atualizar o Edital devido a um erro inesperado: {e}")
                print(f"Erro na atualização do Edital (bloco try/except): {e}")
        else:
            messages.error(request, 'Erro ao atualizar Edital. Verifique os campos.')
            # Seus prints de validação aqui...
            print("====================================")
            print("ERRO DE VALIDAÇÃO DO FORMULÁRIO EDITAL (EDIÇÃO):")
            print("Erros do formulário principal (Edital):", form.errors)
            print("Erros do formset de Lotes:", lotes_formset.errors)
            print("Erros do formset de Itens:", itens_formset.errors)
            print("====================================")
    else: # GET request
        form = EditalForm(instance=edital)
        lotes_formset = LoteFormSet(instance=edital, prefix='lotes')
        itens_formset = ItemLicitadoFormSet(instance=edital, prefix='itens')

    context = {
        'form': form,
        'lotes_formset': lotes_formset,
        'itens_formset': itens_formset,
        'edital': edital,
        'titulo_pagina': f'Editar Edital: {edital.numero_edital}'
    }
    return render(request, 'licitacoes/editar_edital.html', context)

# licitacoes/views.py
def detalhar_edital(request, pk):
    # Otimização: Busca o edital e já inclui os dados de processo_vinculado
    # na mesma consulta SQL, evitando acessos extras ao banco.
    edital = get_object_or_404(
        Edital.objects.select_related('processo_vinculado'),
        pk=pk
    )
    context = {'edital': edital,}
    return render(request, 'licitacoes/detalhar_edital.html', context)



# Nova view para o dashboard de licitações
@login_required
def licitacoes_dashboard(request):
    total_editais = Edital.objects.count()
    editais_publicados = Edital.objects.filter(status='PUBLICADO').count()
    editais_abertos = Edital.objects.filter(status='ABERTO').count()
    # Adicione mais contagens conforme os status do seu modelo Edital

    context = {
        'total_editais': total_editais,
        'editais_publicados': editais_publicados,
        'editais_abertos': editais_abertos,
        'titulo_pagina': 'Dashboard de Licitações',
    }
    return render(request, 'licitacoes/dashboard_licitacoes.html', context)


# <<< NOVAS VIEWS PARA RESULTADO DA LICITAÇÃO >>>
@login_required
def registrar_resultado_licitacao(request, edital_pk):
    edital = get_object_or_404(Edital, pk=edital_pk)


    if request.method == 'POST':
        form = ResultadoLicitacaoForm(request.POST)
        if form.is_valid():
            resultado = form.save(commit=False)
            resultado.edital = edital
            resultado.responsavel_registro = request.user # Associa o usuário logado
            resultado.save()
            messages.success(request, 'Resultado da Licitação registrado com sucesso!')
            return redirect('licitacoes:detalhar_resultado_licitacao', pk=resultado.pk)
        else:
            messages.error(request, 'Erro ao registrar Resultado da Licitação. Verifique os campos.')
            print("Erros do formulário ResultadoLicitacao:", form.errors)
    else:
       
        form = ResultadoLicitacaoForm(edital_instance=edital)

    context = {
        'form': form,
        'edital': edital,
        'titulo_pagina': f'Registrar Resultado para Edital: {edital.numero_edital}',
    }
    return render(request, 'licitacoes/registrar_resultado_licitacao.html', context)

@login_required
def detalhar_resultado_licitacao(request, pk):
    resultado = get_object_or_404(ResultadoLicitacao, pk=pk)

    context = {
        'resultado': resultado,
        'titulo_pagina': f'Detalhes do Resultado: {resultado.edital.numero_edital}',
    }
    return render(request, 'licitacoes/detalhar_resultado_licitacao.html', context)

@login_required
def listar_resultados_licitacao(request):
    resultados = ResultadoLicitacao.objects.all().order_by('-data_homologacao')
    context = {
        'resultados': resultados,
        'titulo_pagina': 'Lista de Resultados de Licitação',
    }
    return render(request, 'licitacoes/listar_resultados_licitacao.html', context)

# SysGov_Project/licitacoes/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Edital, ResultadoLicitacao # Importe o modelo ResultadoLicitacao
from .forms import EditalForm, ResultadoLicitacaoForm # Importe o formulário ResultadoLicitacaoForm

# ... (todas as suas views existentes) ...

# --- NOVA VIEW PARA EDITAR O RESULTADO DA LICITAÇÃO ---
@login_required
@permission_required('licitacoes.change_resultadolicitacao', raise_exception=True)
def editar_resultado_licitacao(request, pk):
    resultado = get_object_or_404(ResultadoLicitacao, pk=pk)

    # Opcional: Adicione verificação de permissão se o usuário é o autor do edital ou superusuário
    if resultado.edital.responsavel_publicacao != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar este Resultado da Licitação.')
        return redirect('licitacoes:detalhar_resultado_licitacao', pk=resultado.pk)

    if request.method == 'POST':
        form = ResultadoLicitacaoForm(request.POST, instance=resultado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resultado da Licitação atualizado com sucesso!')
            return redirect('licitacoes:detalhar_resultado_licitacao', pk=resultado.pk)
        else:
            messages.error(request, 'Erro ao atualizar Resultado da Licitação. Verifique os campos.')
    else:
        form = ResultadoLicitacaoForm(instance=resultado)

    context = {
        'form': form,
        'resultado': resultado,
        'titulo_pagina': f'Editar Resultado da Licitação: {resultado.edital.numero_edital}'
    }
    return render(request, 'licitacoes/editar_resultado_licitacao.html', context)




@login_required
def painel_pregao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    
    if request.method == 'POST':
        if 'submit_participante' in request.POST:
            if pregao.status in ['AGENDADO', 'ABERTO_PARA_LANCES']:
                form_participante = ParticipanteForm(request.POST)
                if form_participante.is_valid():
                    participante = form_participante.save(commit=False)
                    participante.pregao = pregao
                    try:
                        participante.save()
                        messages.success(request, f"Fornecedor '{participante.fornecedor.razao_social}' credenciado.")
                    except IntegrityError:
                        messages.error(request, 'Este fornecedor já está credenciado.')
            else:
                messages.error(request, 'Não é possível credenciar participantes. O pregão já foi iniciado ou finalizado.')

        elif 'submit_lance' in request.POST:
            if pregao.status == 'EM_DISPUTA':
                form_lance = LanceForm(request.POST, pregao=pregao)
                if form_lance.is_valid():
                    form_lance.save()
                    messages.success(request, 'Lance registado com sucesso.')
                else:
                    messages.error(request, 'Erro ao registar o lance.')
            else:
                messages.error(request, 'Não é possível registar lances. O pregão não está em disputa.')

        elif 'acao_sessao' in request.POST:
            acao = request.POST.get('acao_sessao')
            if request.user == pregao.pregoeiro:
                if acao == 'iniciar_disputa' and pregao.status in ['AGENDADO', 'ABERTO_PARA_LANCES']:
                    pregao.status = 'EM_DISPUTA'
                    pregao.save()
                    messages.success(request, 'A sessão de disputa foi iniciada!')
                elif acao == 'encerrar_sessao' and pregao.status == 'EM_DISPUTA':
                    pregao.status = 'FINALIZADO'
                    pregao.data_encerramento_sessao = timezone.now()
                    pregao.save()
                    messages.success(request, 'A sessão do pregão foi finalizada.')
            else:
                messages.error(request, 'Apenas o pregoeiro responsável pode controlar a sessão.')

        elif 'aceitar_lance' in request.POST:
            if request.user == pregao.pregoeiro and pregao.status == 'EM_DISPUTA':
                with transaction.atomic():
                    lance_id = request.POST.get('lance_id')
                    lance_vencedor = get_object_or_404(Lance, pk=lance_id)
                    if lance_vencedor.participante.pregao == pregao:
                        item_licitado = lance_vencedor.item
                        item_licitado.lances.exclude(pk=lance_vencedor.pk).update(aceito=False)
                        lance_vencedor.aceito = True
                        lance_vencedor.save()
                        messages.success(request, f"Lance de R$ {lance_vencedor.valor_lance} aceite como novo vencedor.")
            else:
                messages.error(request, "Apenas o pregoeiro pode aceitar lances nesta fase.")
        
        elif 'gerar_resultados' in request.POST:
            if request.user == pregao.pregoeiro and pregao.status == 'FINALIZADO':
                lances_vencedores = Lance.objects.filter(participante__pregao=pregao, aceito=True)
                if not lances_vencedores.exists():
                    messages.warning(request, 'Nenhum lance vencedor foi selecionado para gerar resultados.')
                else:
                    resultados_criados = 0
                    with transaction.atomic():
                        for lance in lances_vencedores:
                            ResultadoLicitacao.objects.update_or_create(
                                edital=pregao.edital, item_licitado=lance.item,
                                defaults={
                                    'fornecedor_vencedor': lance.participante.fornecedor.razao_social,
                                    'cnpj_vencedor': lance.participante.fornecedor.cnpj,
                                    'valor_homologado': lance.valor_lance,
                                    'data_homologacao': timezone.now().date(),
                                    'responsavel_registro': request.user
                                }
                            )
                            resultados_criados += 1
                    messages.success(request, f'{resultados_criados} resultado(s) de licitação foram gerados/atualizados.')
            else:
                messages.error(request, 'Ação não permitida.')

        return redirect('licitacoes:painel_pregao', pregao_id=pregao.id)

    # Lógica para GET
    participantes = pregao.participantes.all().order_by('fornecedor__razao_social')
    itens_edital = pregao.edital.itens_diretos.all().prefetch_related('lances__participante__fornecedor')
    form_participante = ParticipanteForm()
    form_lance = LanceForm(pregao=pregao)
    
    context = {
        'pregao': pregao, 'participantes': participantes, 'itens_edital': itens_edital,
        'form_participante': form_participante, 'form_lance': form_lance,
        'titulo_pagina': f"Painel do Pregão - Edital {pregao.edital.numero_edital}"
    }
    return render(request, 'licitacoes/painel_pregao.html', context)



@login_required
def gerar_ata_pregao_pdf(request, pregao_id):
    """
    Gera o documento oficial da Ata da Sessão do Pregão em formato PDF.
    """
    try:
        pregao = get_object_or_404(Pregao, pk=pregao_id)
        
        context = {
            'pregao': pregao
            # Todos os dados necessários (participantes, itens, lances)
            # já são acessíveis no template através do objeto 'pregao'.
        }

        # 1. Renderiza o nosso template HTML para uma string
        html_string = render_to_string('licitacoes/ata_pregao_pdf.html', context)
        
        # 2. Converte a string HTML para PDF
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        
        # 3. Cria a resposta HTTP para o navegador
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Ata_Pregao_{pregao.edital.numero_edital}.pdf"'
        
        return response

    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao gerar o PDF da Ata: {e}")
        return redirect('licitacoes:painel_pregao', pregao_id=pregao_id)
    
    
@login_required
def analise_edital_ia_view(request):
    resultado_analise = None
    if request.method == 'POST' and 'edital_file' in request.FILES:
        edital_file = request.FILES['edital_file']
        texto_edital = ""

        try:
            if edital_file.name.endswith('.pdf'):
                reader = PyPDF2.PdfReader(edital_file)
                for page in reader.pages:
                    texto_edital += page.extract_text()
            elif edital_file.name.endswith('.txt'):
                texto_edital = edital_file.read().decode('utf-8')

            # Chama a nova função para analisar o edital
            resultado_analise = ai_services.analisar_edital_com_ia(texto_edital)

        except Exception as e:
            resultado_analise = f"Ocorreu um erro ao processar o arquivo: {e}"

    context = {
        'resultado_analise': resultado_analise,
        'titulo_pagina': 'Análise de Edital com IA'
    }
    return render(request, 'licitacoes/ia_analise_edital.html', context)


@login_required
def licitacoes_dashboard(request):
    """
    Exibe um painel com informações resumidas sobre as licitações.
    """
    editais_recentes = Edital.objects.all().order_by('-data_publicacao')[:5]
    pregoes_recentes = Pregao.objects.all().order_by('-data_abertura_sessao')[:5]
    
    context = {
        'editais_recentes': editais_recentes,
        'pregoes_recentes': pregoes_recentes,
        'titulo_pagina': 'Dashboard de Licitações'
    }
    return render(request, 'licitacoes/dashboard_licitacoes.html', context)

# licitacoes/views.py
from django.contrib import messages
from licitacoes.models import Edital # O modelo está como 'Edital' no seu models.py
from integracao_audesp.mappers import formatar_edital_para_audesp
from integracao_audesp.client import AudespClient
from integracao_audesp.exceptions import AudespAPIError
from django.http import HttpResponse # Adicione esta também, pois é usada na mesma view
import PyPDF2 # Verifique se já importou esta
from weasyprint import HTML
from django.template.loader import render_to_string

@login_required # Adicionar o decorator para segurança
def enviar_licitacao_view(request, licitacao_id): # <-- CORRIGIDO AQUI
       
    # Adicionamos esta verificação para garantir que a view só seja chamada via POST
    if request.method != 'POST':
        messages.error(request, "Ação não permitida.")
        return redirect('licitacoes:detalhar_edital', pk=licitacao_id)
    
    edital = get_object_or_404(Edital, id=licitacao_id) # <-- E AQUI também
    
    if not edital.arquivo_edital:
        messages.warning(request, "Não é possível enviar para a Audesp. O arquivo PDF do edital não foi anexado.")
        return redirect('licitacoes:detalhar_edital', pk=licitacao_id)
    
    try:
        # 1. Mapear os dados
        print("Mapeando dados do edital...")
        dados_para_envio = formatar_edital_para_audesp(edital)
        
        # 2. Enviar para a Audesp
        print("Iniciando envio para Audesp...")
        cliente = AudespClient()
        resultado = cliente.enviar_edital(dados_para_envio, edital.arquivo_edital.path) # Supondo que o campo é 'arquivo_edital'
        
        # 3. Tratar o resultado de SUCESSO
        protocolo = resultado.get('protocolo')
        print(f"Envio bem-sucedido! Protocolo: {protocolo}")

        # Salve o protocolo no seu modelo (você precisará criar este campo)
        # edital.protocolo_audesp = protocolo
        # edital.status_audesp = 'ENVIADO'
        # edital.save()

        messages.success(request, f"Edital enviado com sucesso para a Audesp! Protocolo: {protocolo}")

    except AudespAPIError as e:
        # 4. Tratar o resultado de ERRO
        print(f"ERRO na integração com Audesp: {e}")
        # Monta uma mensagem de erro detalhada para o usuário
        error_message = f"Falha ao enviar para Audesp: {e.message}"
        if e.status_code:
            error_message += f" (Status: {e.status_code} - Resposta: {e.response_text})"
        
        messages.error(request, error_message)

    except Exception as e:
        # Pega qualquer outro erro inesperado
        print(f"ERRO inesperado na view de envio: {e}")
        messages.error(request, f"Ocorreu um erro inesperado no sistema: {e}")

    # Redireciona de volta para a página de detalhes do edital
    return redirect('licitacoes:detalhar_edital', pk=edital.pk)


# licitacoes/views.py

# ... (seus outros imports no topo do arquivo) ...
from integracao_audesp.mappers import formatar_edital_para_audesp # Importe seu mapeador

# licitacoes/views.py

# ... outros imports
from integracao_audesp.views import gerar_edital_audesp_json # IMPORTANTE: Importa sua view
import json

@login_required
def conferencia_envio_audesp(request, licitacao_id):
    edital = get_object_or_404(Edital, pk=licitacao_id)

    try:
        # Chama a SUA view original para gerar o JSON
        json_response = gerar_edital_audesp_json(request, edital_id=edital.pk)
        # Converte o conteúdo do JsonResponse para um dicionário Python
        dados_formatados_para_audesp = json.loads(json_response.content)
    except Exception as e:
        messages.error(request, f"Erro ao preparar os dados para envio: {e}")
        return redirect('integracao_audesp:painel_audesp')

    context = {
        'edital': edital,
        'dados_formatados': dados_formatados_para_audesp,
        'titulo_pagina': f'Conferência de Envio - Edital {edital.numero_edital}'
    }
    return render(request, 'licitacoes/conferencia_envio.html', context)