# SysGov_Project/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse # Para retornar o HTML para AJAX
from django.template.loader import render_to_string # Para renderizar templates como string
from django.contrib import messages
from django.db.models.functions import TruncMonth
# Importações dos modelos e formulários do próprio app 'core'
from .models import Processo, ArquivoAnexo, Fornecedor,Notificacao
from .forms import ProcessoForm, ArquivoAnexoForm,FornecedorForm
from django.db.models import Sum, Count, F, Func,Q
# Importe os modelos necessários dos outros apps (agora que estão no mesmo projeto)
from contratacoes.models import ETP, TR
from licitacoes.models import Edital
from financeiro.models import DocumentoFiscal, Pagamento
from django.contrib.contenttypes.models import ContentType
import json 
from contratacoes.models import Contrato, ETP, TR
from licitacoes.models import Edital, ResultadoLicitacao
from financeiro.models import Pagamento
import os
from django.conf import settings # Importar settings para acessar STATIC_ROOT ou MEDIA_ROOT


def visualizar_anexo_pdf(request, anexo_id):
    anexo = get_object_or_404(ArquivoAnexo, pk=anexo_id)
    
    # !!! VERIFIQUE SE O CAMPO 'arquivo' NO SEU MODELO ArquivoAnexo TEM UM VALOR !!!
    # Se 'arquivo' for um FileField e estiver vazio para este anexo, anexo.arquivo pode ser None.
    if not anexo.arquivo: 
        raise Http404("Arquivo PDF não anexado para este item.")

    file_path = anexo.arquivo.path # Este é o caminho completo do arquivo no sistema de arquivos
    
    # Adicione este print para depuração (vai aparecer no terminal do Django)
    print(f"Tentando abrir arquivo em: {file_path}")

    if not os.path.exists(file_path):
        # Se o arquivo não existir no disco, é um 404
        raise Http404("O arquivo não existe no sistema de arquivos do servidor.")

    # Verifica se o arquivo é um PDF antes de tentar servi-lo como tal
    # Isso é opcional, mas ajuda a evitar erros se for outro tipo de arquivo
    if not anexo.arquivo.name.lower().endswith('.pdf'):
         return HttpResponse("Este arquivo não é um PDF.", status=400) # Bad Request

    with open(file_path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        # Opcional: Adicione um cabeçalho para nomear o arquivo no download
        # response['Content-Disposition'] = f'inline; filename="{anexo.arquivo.name}"' # 'inline' para abrir no navegador, 'attachment' para baixar
        return response
    

def home(request): # O nome da sua URL pode apontar para 'home_view', certifique-se de que os nomes correspondem
    dashboard_stats = {}
    labels_fornecedores = []
    data_fornecedores = []

    # A lógica do dashboard só é executada para usuários logados
    if request.user.is_authenticated:
        # 1. Lógica para as estatísticas dos cartões
        dashboard_stats = {
            'processos_em_analise': Processo.objects.filter(status='EM_ANALISE').count(),
            'licitacoes_abertas': Edital.objects.filter(status='ABERTO').count(),
            'contratos_vigentes': Contrato.objects.filter(status='VIGENTE').count(),
            'pagamentos_pendentes': 0 # Lógica a ser implementada no futuro
        }
        
        # 2. Lógica para preparar os dados do gráfico de Top Fornecedores
        top_fornecedores_data = Contrato.objects.values('contratado__razao_social') \
            .annotate(total_valor=Sum('valor_total')) \
            .order_by('-total_valor')[:5]

        labels_fornecedores = [item['contratado__razao_social'] for item in top_fornecedores_data]
        data_fornecedores = [float(item['total_valor']) for item in top_fornecedores_data]

    # 3. Todos os dados são enviados para o template no 'context'
    context = {
        'dashboard_stats': dashboard_stats,
        'labels_fornecedores': json.dumps(labels_fornecedores), # Enviamos como JSON
        'data_fornecedores': json.dumps(data_fornecedores),   # Enviamos como JSON
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard_gerencial_view(request):
    """Coleta e prepara os dados para o dashboard gerencial com múltiplos gráficos."""
    # Gráfico 1: Distribuição de ETPs por Status
    status_data = ETP.objects.values('status').annotate(count=Count('id')).order_by('status')
    status_display_map = dict(ETP._meta.get_field('status').choices)
    labels_status = [status_display_map.get(item['status'], item['status']) for item in status_data]
    data_status = [item['count'] for item in status_data]

    # Gráfico 2: Top 5 Fornecedores por Valor Contratado
    top_fornecedores_data = Contrato.objects.values('contratado__razao_social') \
        .annotate(total_valor=Sum('valor_total')) \
        .order_by('-total_valor')[:5]
    labels_fornecedores = [item['contratado__razao_social'] for item in top_fornecedores_data]
    data_fornecedores = [float(item['total_valor']) for item in top_fornecedores_data]

    # Gráfico 3: Economia Média Mensal em Licitações
    economia_mensal_data = ResultadoLicitacao.objects.filter(valor_estimado_inicial__isnull=False, valor_homologado__isnull=False) \
        .annotate(mes=TruncMonth('data_homologacao')) \
        .values('mes') \
        .annotate(economia_total=Sum(F('valor_estimado_inicial') - F('valor_homologado')), num_licitacoes=Count('id')) \
        .order_by('mes')
    labels_economia = [item['mes'].strftime('%b/%Y') for item in economia_mensal_data]
    data_economia = [float(item['economia_total'] / item['num_licitacoes']) if item['num_licitacoes'] > 0 else 0 for item in economia_mensal_data]

    context = {
        'titulo_pagina': 'Dashboard Gerencial',
        'labels_status': json.dumps(labels_status),
        'data_status': json.dumps(data_status),
        'labels_fornecedores': json.dumps(labels_fornecedores),
        'data_fornecedores': json.dumps(data_fornecedores),
        'labels_economia': json.dumps(labels_economia),
        'data_economia': json.dumps(data_economia),
    }
    return render(request, 'core/dashboard_gerencial.html', context)

# --- GESTÃO DE PROCESSOS ---

@login_required
def meus_processos_view(request):
    """
    Lista os processos com base no perfil do utilizador e permite a filtragem.
    """
    is_manager = request.user.is_superuser or request.user.groups.filter(name__in=['Analise de Requerimentos', 'Setor de Orcamento', 'Comissao de Licitacao']).exists()

    if is_manager:
        processos_list = Processo.objects.all()
        titulo_pagina = "Todos os Processos do Sistema"
    else:
        processos_list = Processo.objects.filter(usuario=request.user)
        titulo_pagina = "Meus Processos"

    query = request.GET.get('q')
    status_filter = request.GET.get('status')
    if query:
        processos_list = processos_list.filter(Q(titulo__icontains=query) | Q(numero_protocolo__icontains=query))
    if status_filter:
        processos_list = processos_list.filter(status=status_filter)

    context = {
        'processos': processos_list.order_by('-data_criacao'),
        'status_choices': Processo.STATUS_CHOICES,
        'query_atual': query or "",
        'status_atual': status_filter or "",
        'titulo_pagina': titulo_pagina
    }
    return render(request, 'core/meus_processos.html', context)


# View para Criar um Novo Processo
@login_required(login_url='/accounts/login/')
def criar_processo_view(request):
    if request.method == 'POST':
        form = ProcessoForm(request.POST)
        if form.is_valid():
            processo = form.save(commit=False)
            processo.usuario = request.user
            processo.save()
            messages.success(request, 'Processo criado com sucesso!')
            return redirect('meus_processos')
    else:
        form = ProcessoForm()
    context = {
        'form': form,
        'titulo_pagina': 'Criar Novo Processo'
    }
    return render(request, 'core/criar_processo.html', context)


@login_required(login_url='/accounts/login/')
def detalhes_processo_view(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    
    # Busca o ETP associado (se existir)
    try:
        etp = processo.etp_documento
    except ETP.DoesNotExist:
        etp = None

    # Busca o TR associado (se existir)
    try:
        tr = processo.tr_documento
    except TR.DoesNotExist:
        tr = None
        
    # Busca o Edital associado (se existir)
    try:
        # Nota: 'edital_licitacao' é um exemplo de related_name. Ajuste se o seu for diferente.
        edital = processo.edital_licitacao
    except Edital.DoesNotExist:
        edital = None

    # Busca TODOS os contratos vinculados a este processo
    contratos = processo.contratos.all()
    atas_rp = processo.atas_rp.all()
    # Busca os anexos genéricos do processo
    processo_content_type = ContentType.objects.get_for_model(Processo)
    anexos_do_processo = ArquivoAnexo.objects.filter(
        content_type=processo_content_type,
        object_id=processo.id
    ).order_by('-data_upload')

    context = {
        'processo': processo,
        'etp': etp,
        'tr': tr,
        'edital': edital,
        'contratos': contratos,
        'atas_rp': atas_rp,
        'anexos_do_processo': anexos_do_processo,
        'titulo_pagina': f"Painel do Processo {processo.numero_protocolo or ''}"
    }
    return render(request, 'core/detalhes_processo.html', context)


# View para Adicionar Anexo a um Processo
@login_required(login_url='/accounts/login/')
def adicionar_anexo_ao_processo(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    
    if request.method == 'POST':
        form = ArquivoAnexoForm(request.POST, request.FILES)
        if form.is_valid():
            anexo = form.save(commit=False)
            anexo.uploaded_by = request.user
            anexo.content_object = processo
            anexo.save()
            messages.success(request, 'Anexo adicionado ao processo com sucesso!')
            return redirect('detalhes_processo', processo_id=processo.id)
        else:
            messages.error(request, 'Erro ao adicionar anexo. Verifique o formulário.')
    else: # GET request
        form = ArquivoAnexoForm()
    
    # <<< AJUSTE AQUI: Use lógica Python para o valor padrão >>>
    numero_protocolo_display = processo.numero_protocolo if processo.numero_protocolo else "N/A" # <<< ESTA LINHA FOI ADICIONADA/AJUSTADA
    
    context = {
        'form': form,
        'processo': processo,
        'titulo_pagina': f'Adicionar Anexo ao Processo {numero_protocolo_display}' # <<< Use a variável ajustada
    }
    return render(request, 'core/adicionar_anexo_processo.html', context)


# --- VIEWS PARA RENDERIZAR SNIPPETS DE DOCUMENTOS VIA AJAX ---
# Estas views retornam apenas o HTML dos detalhes de um documento para a visualização dinâmica
@login_required
def render_etp_detail_snippet(request, pk):
    etp = get_object_or_404(ETP, pk=pk)
    if etp.processo_vinculado and etp.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este ETP.", status=403)
    
    html_content = render_to_string('core/snippets/etp_detail_snippet.html', {'etp': etp, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_tr_detail_snippet(request, pk):
    tr = get_object_or_404(TR, pk=pk)
    if tr.processo_vinculado and tr.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este TR.", status=403)
    
    html_content = render_to_string('core/snippets/tr_detail_snippet.html', {'tr': tr, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_edital_detail_snippet(request, pk):
    edital = get_object_or_404(Edital, pk=pk)
    if edital.processo_vinculado and edital.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Edital.", status=403)
    
    html_content = render_to_string('core/snippets/edital_detail_snippet.html', {'edital': edital, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_df_detail_snippet(request, pk):
    df = get_object_or_404(DocumentoFiscal, pk=pk)
    if df.processo_vinculado and df.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Documento Fiscal.", status=403)
        
    html_content = render_to_string('core/snippets/df_detail_snippet.html', {'df': df, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_pagamento_detail_snippet(request, pk):
    pg = get_object_or_404(Pagamento, pk=pk)
    if pg.processo_vinculado and pg.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Pagamento.", status=403)
        
    html_content = render_to_string('core/snippets/pagamento_detail_snippet.html', {'pagamento': pg, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_arquivo_anexo_detail_snippet(request, pk):
    anexo = get_object_or_404(ArquivoAnexo, pk=pk)
    # GFK: Verifique se o processo vinculado ao anexo pertence ao usuário logado
    # Esta verificação é importante para segurança.
    if anexo.content_type.model == 'processo' and anexo.content_object.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este anexo.", status=403)
    
    # <<< AJUSTE AQUI: Passe o 'request' ao render_to_string >>>
    html_content = render_to_string('core/snippets/arquivo_anexo_detail_snippet.html', {'anexo': anexo}, request=request)
    return HttpResponse(html_content)


@login_required
def listar_fornecedores(request):
    fornecedores = Fornecedor.objects.all().order_by('razao_social')
    context = {
        'fornecedores': fornecedores,
        'titulo_pagina': 'Cadastro de Fornecedores'
    }
    return render(request, 'core/listar_fornecedores.html', context)

@login_required
def criar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('listar_fornecedores')
    else:
        form = FornecedorForm()

    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Fornecedor'
    }
    return render(request, 'core/criar_fornecedor.html', context)


# Em core/views.py

@login_required
def detalhar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    # Buscamos os contratos e empenhos relacionados a este fornecedor
    contratos = fornecedor.contratos.all()
    empenhos = fornecedor.empenhos.all()
    context = {
        'fornecedor': fornecedor,
        'contratos': contratos,
        'empenhos': empenhos,
        'titulo_pagina': f'Detalhes de {fornecedor.razao_social}'
    }
    return render(request, 'core/detalhar_fornecedor.html', context)


# Em core/views.py

@login_required
def editar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados do fornecedor atualizados com sucesso!')
            return redirect('detalhar_fornecedor', pk=fornecedor.pk)
    else:
        form = FornecedorForm(instance=fornecedor)

    context = {
        'form': form,
        'fornecedor': fornecedor,
        'titulo_pagina': 'Editar Fornecedor'
    }
    return render(request, 'core/editar_fornecedor.html', context)



def manual_do_sistema_view(request):
    """
    Renderiza a página do manual interativo do sistema.
    """
    context = {
        'titulo_pagina': 'Manual do Sistema SysGov'
    }
    return render(request, 'core/manual_do_sistema.html', context)


@login_required
def busca_global_view(request):
    """
    Realiza uma busca em múltiplos modelos e exibe os resultados.
    """
    query = request.GET.get('q', '')
    
    # Listas para guardar os resultados de cada tipo de documento
    resultados_processos = []
    resultados_etps = []
    resultados_contratos = []
    resultados_fornecedores = []
    
    if query:
        # Busca em Processos (por título ou protocolo)
        resultados_processos = Processo.objects.filter(
            Q(titulo__icontains=query) | Q(numero_protocolo__icontains=query)
        )
        
        # Busca em ETPs (por título ou número do processo)
        resultados_etps = ETP.objects.filter(
            Q(titulo__icontains=query) | Q(numero_processo__icontains=query)
        )
        
        # Busca em Contratos (por objeto, número ou nome do fornecedor)
        resultados_contratos = Contrato.objects.filter(
            Q(objeto__icontains=query) | 
            Q(numero_contrato__icontains=query) |
            Q(contratado__razao_social__icontains=query)
        )
        
        # Busca em Fornecedores (por razão social ou CNPJ)
        resultados_fornecedores = Fornecedor.objects.filter(
            Q(razao_social__icontains=query) | Q(cnpj__icontains=query)
        )

    context = {
        'query': query,
        'resultados_processos': resultados_processos,
        'resultados_etps': resultados_etps,
        'resultados_contratos': resultados_contratos,
        'resultados_fornecedores': resultados_fornecedores,
        'total_resultados': len(resultados_processos) + len(resultados_etps) + len(resultados_contratos) + len(resultados_fornecedores),
        'titulo_pagina': f"Resultados da Busca por '{query}'"
    }
    
    return render(request, 'core/busca_resultados.html', context)


@login_required
def marcar_notificacao_como_lida(request, notificacao_id):
    """
    Encontra uma notificação, marca-a como lida e redireciona o utilizador
    para o link de ação original da notificação.
    """
    # Garante que estamos a marcar uma notificação que pertence ao utilizador logado
    notificacao = get_object_or_404(Notificacao, pk=notificacao_id, usuario_destino=request.user)
    
    if not notificacao.lida:
        notificacao.lida = True
        notificacao.save()
    
    if notificacao.link_acao:
        return redirect(notificacao.link_acao)
    else:
        return redirect('core:home')