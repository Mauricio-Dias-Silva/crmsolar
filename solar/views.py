import logging
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.db.models import Count, Sum
from django.db import transaction
from django.utils.text import slugify
from django.http import JsonResponse, HttpResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_POST
import json # Adicionado para corrigir o erro no dashboard_projetos
from django.core.paginator import Paginator
from django.db.models import Q # Importamos o Q para buscas complexas
from django.conf import settings
from django.contrib.auth import get_user_model
from produtos.services import analisar_imagem_produto
from django.urls import reverse
from urllib.parse import urlencode

User = get_user_model()

# Importa os modelos do app 'solar'
from .models import Cliente, Projeto, Etapa, Material, Fornecedor, Financeiro, \
    LancamentoFinanceiro, DocumentoProjeto, Usuario, Departamento, MenuPermissao

# Importa os formulários do app 'solar'
from .forms import ProjetoForm, ClienteForm, EtapaForm, MaterialForm, FornecedorForm, \
    LancamentoFinanceiroForm, DocumentoProjetoForm, UsuarioCreateForm, UsuarioUpdateForm, \
    ProdutoEcommerceForm, PerfilClienteForm

# Importa os modelos do app 'produtos' para uso direto nas views
from produtos.models import Produto, ProdutoImage, Pedido # Adicionado Pedido para a lógica de pedidos

logger = logging.getLogger(__name__)

# --- FUNÇÕES DE TESTE PARA DECORADORES ---
def pode_acessar_crm(user):
    return user.is_authenticated and user.is_active and (user.is_staff or user.is_superuser or user.is_crm_staff)

def pode_acessar_ecommerce(user):
    return user.is_authenticated and user.is_active and (user.is_customer or user.is_crm_staff or user.is_superuser)

# ------------------------------------------------------------------
# VIEWS DE AUTENTICAÇÃO
# ------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        if request.user.pode_acessar_crm:
            return redirect('crm:home')
        else:
            messages.warning(request, "Você não tem acesso à área do CRM com esta conta. Por favor, faça login com uma conta de CRM.")
            logout(request)
            return redirect('login_crm')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.pode_acessar_crm:
                login(request, user)
                messages.success(request, f"Bem-vindo(a) à área do CRM, {user.username}!")
                return redirect('crm:home')
            else:
                messages.error(request, 'Usuário ou senha inválidos ou você não tem permissão para acessar o CRM!')
        else:
            messages.error(request, 'Por favor, preencha todos os campos corretamente!')
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form, 'titulo': 'Login do CRM Solar'})


def login_ecommerce_view(request):
    if request.user.is_authenticated:
        if request.user.is_customer:
            return redirect('crm:cliente_dashboard')
        else:
            return redirect('produtos:home')
        
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Bem-vindo(a) de volta, {user.username}!")
                if user.is_customer:
                    return redirect('crm:cliente_dashboard')
                else:
                    return redirect('produtos:home')
            else:
                messages.error(request, 'Credenciais inválidas.')
        else:
            messages.error(request, 'Por favor, preencha o nome de usuário e a senha.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'titulo': 'Login do E-commerce'})

@login_required 
def logout_view(request):
    logout(request)
    messages.info(request, "Você foi desconectado(a) com sucesso.")
    return redirect('produtos:home') 

# ------------------------------------------------------------------
# NOVA VIEW: Registro de Usuário E-commerce (Cria Usuario e Cliente)
# ------------------------------------------------------------------
def register_ecommerce_user(request):
    if request.user.is_authenticated:
        messages.info(request, "Você já está logado(a).")
        return redirect('produtos:home')

    if request.method == 'POST':
        user_form = UsuarioCreateForm(request.POST) 
        cliente_form = PerfilClienteForm(request.POST) 

        if 'password_confirm' in user_form.fields:
            pass

        if user_form.is_valid() and cliente_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.is_customer = True
                    user.is_active = True
                    user.set_password(user_form.cleaned_data['password'])
                    user.save()

                    cliente = cliente_form.save(commit=False)
                    cliente.usuario = user
                    cliente.save()

                    login(request, user)
                    messages.success(request, 'Seu cadastro foi realizado com sucesso! Bem-vindo(a) à Solar Shop.')
                    
                    return redirect('produtos:home') 

            except ValidationError as e:
                messages.error(request, f"Erro de validação: {e.message}")
            except Exception as e:
                logger.error(f"Erro no cadastro de e-commerce: {e}", exc_info=True)
                messages.error(request, f'Ocorreu um erro inesperado no cadastro. Por favor, tente novamente.')
        else:
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"Usuário - {user_form.fields[field].label}: {error}")
            for field, errors in cliente_form.errors.items():
                for error in errors:
                    messages.error(request, f"Cliente - {cliente_form.fields[field].label}: {error}")
    else:
        user_form = UsuarioCreateForm()
        cliente_form = PerfilClienteForm()

    context = {
        'user_form': user_form,
        'cliente_form': cliente_form,
        'titulo': 'Cadastre-se na Solar Shop'
    }
    return render(request, 'registration/register.html', context)


# ------------------------------------------------------------------
# VIEWS GERAIS DO CRM
# ------------------------------------------------------------------
@login_required
@user_passes_test(pode_acessar_crm)
def home(request):
    return render(request, 'solar/home.html')

@login_required
@user_passes_test(pode_acessar_crm)
def dashboard_projetos(request):
    projetos = Projeto.objects.all()
    total_projetos = projetos.count()
    em_andamento = projetos.filter(status="Em andamento").count()

    status_qs = projetos.values('status').annotate(total=Count('id'))
    status_labels = [s['status'] for s in status_qs]
    status_data = [s['total'] for s in status_qs]

    cliente_qs = projetos.values('cliente__nome').annotate(total=Count('id'))
    cliente_labels = [c['cliente__nome'] for c in cliente_qs]
    cliente_data = [c['total'] for c in cliente_qs]

    ultimos_projetos = projetos.order_by('-data_inicio')[:5]

    context = {
        'total_projetos': total_projetos,
        'em_andamento': em_andamento,
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'cliente_labels': json.dumps(cliente_labels),
        'cliente_data': json.dumps(cliente_data),
        'ultimos_projetos': ultimos_projetos,
    }
    return render(request, 'solar/dashboard_projetos.html', context)

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.add_documentoprojeto', raise_exception=True)
def upload_documento_projeto(request, projeto_id):
    projeto = get_object_or_404(Projeto, pk=projeto_id)
    if request.method == 'POST':
        form = DocumentoProjetoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.projeto = projeto
            doc.save()
            messages.success(request, 'Documento enviado com sucesso!')
            return redirect('crm:detalhe_projeto', pk=projeto.id)
        else:
            messages.error(request, 'Erro ao enviar documento. Verifique os campos.')
    else:
        form = DocumentoProjetoForm()
    return render(request, 'solar/upload_documento_projeto.html', {'form': form, 'projeto': projeto})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.delete_documentoprojeto', raise_exception=True)
def excluir_documento_projeto(request, projeto_id, doc_id):
    projeto = get_object_or_404(Projeto, id=projeto_id)
    doc = get_object_or_404(DocumentoProjeto, id=doc_id, projeto=projeto)
    if request.method == 'POST':
        doc.arquivo.delete()
        doc.delete()
        messages.success(request, 'Documento excluído com sucesso!')
        return redirect('crm:detalhe_projeto', pk=projeto.id)
    return render(request, 'solar/confirmar_exclusao_documento.html', {'documento': doc, 'projeto': projeto})

# ------------------------------------------------------------------
# VIEWS DE CLIENTES (CRM)
# ------------------------------------------------------------------
@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_cliente', raise_exception=True)
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'solar/lista_clientes.html', {'clientes': clientes})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_cliente', raise_exception=True)
def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'solar/detalhe_cliente.html', {'cliente': cliente})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.add_cliente', raise_exception=True)
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('crm:lista_clientes')
        else:
            messages.error(request, 'Erro ao cadastrar cliente. Verifique os campos.')
    else:
        form = ClienteForm()
    return render(request, 'solar/cadastrar_cliente.html', {'form': form})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.change_cliente', raise_exception=True)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('crm:detalhe_cliente', pk=cliente.pk)
        else:
            messages.error(request, 'Erro ao atualizar cliente. Verifique os campos.')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'solar/editar_cliente.html', {'form': form, 'cliente': cliente})

@login_required
@user_passes_test(pode_acessar_crm)

def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == "POST":
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f"Cliente '{nome}' foi excluído com sucesso.")
        return redirect('crm:lista_clientes')

    return render(request, 'solar/confirmar_exclusao_cliente.html', {'cliente': cliente})



@login_required
def cliente_painel_detalhe(request, pk):
    """
    Exibe os detalhes de um único projeto para o cliente logado.
    """
    try:
        # Tenta obter o perfil do cliente associado ao usuário logado
        cliente_logado = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.warning(request, "Por favor, complete seu perfil de cliente.")
        return redirect('crm:completar_perfil_cliente')

    # Busca o projeto pelo ID (pk) E garante que ele pertence ao cliente logado
    projeto = get_object_or_404(Projeto, pk=pk, cliente=cliente_logado)

    # Lógica para calcular o progresso
    total_etapas = projeto.etapas.count()
    etapas_concluidas = projeto.etapas.filter(status='Concluído').count()
    percentual = 0
    if total_etapas > 0:
        percentual = int((etapas_concluidas / total_etapas) * 100)

    # Lógica para o financeiro
    total_pago = Financeiro.objects.filter(projeto=projeto, status='Pago').aggregate(Sum('valor'))['valor__sum'] or 0
    total_pendente = (projeto.valor_total or 0) - total_pago
    
    context = {
        'projeto': projeto,
        'percentual': percentual,
        'total_etapas': total_etapas,
        'etapas_concluidas': etapas_concluidas,
        'total_pago': total_pago,
        'total_pendente': total_pendente,
    }

    # Esta view renderiza o template de detalhe de um único projeto
    return render(request, 'solar/cliente_painel.html', context)
# ------------------------------------------------------------------
# VIEWS DE PROJETOS (CRM)
# ------------------------------------------------------------------

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_projeto', raise_exception=True)
def lista_projetos(request):
    # 1. Começamos com a consulta otimizada, ordenando pelos mais recentes
    queryset = Projeto.objects.select_related('cliente', 'responsavel').order_by('-data_inicio')

    # 2. Aplicamos filtros baseados na URL (ex: ?status=Concluído)
    filtro_status = request.GET.get('status')
    if filtro_status:
        queryset = queryset.filter(status=filtro_status)

    # 3. Aplicamos a busca (ex: ?q=Solar)
    termo_busca = request.GET.get('q')
    if termo_busca:
        # Busca no nome OU na descrição do projeto
        queryset = queryset.filter(
            Q(nome__icontains=termo_busca) | 
            Q(descricao__icontains=termo_busca)
        )

    # 4. Adicionamos a paginação no final, após todos os filtros
    paginador = Paginator(queryset, 20) # 20 projetos por página
    numero_da_pagina = request.GET.get('page')
    projetos = paginador.get_page(numero_da_pagina)

    context = {
        'projetos': projetos,
        'statuses': Projeto._meta.get_field('status').choices # Para popular um dropdown de filtro
    }

    return render(request, 'solar/lista_projetos.html', context)



@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_projeto', raise_exception=True)
def detalhe_projeto(request, pk):
    # MUDANÇA AQUI: Adicionamos o prefetch_related para buscar as etapas
    # e documentos de forma otimizada, tudo de uma vez.
    projeto = get_object_or_404(
        Projeto.objects.prefetch_related('etapas', 'documentos'), 
        pk=pk
    )

    context = {
        'projeto': projeto,
    }
    
    return render(request, 'solar/detalhe_projeto.html', context)

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.add_projeto', raise_exception=True)
def cadastrar_projeto(request):
    documentos_labels = [
        'RG', 'CPF/CNH', 'Conta de Luz',
        'Comprovante de Residência', 'Foto do Poste'
    ]
    if request.method == 'POST':
        form = ProjetoForm(request.POST, request.FILES)
        if form.is_valid():
            projeto = form.save()
            for i in range(1, 6):
                arquivo = request.FILES.get(f'documento_arquivo_{i}')
                nome = request.POST.get(f'documento_nome_{i}', f'Documento {i}')
                visivel = request.POST.get(f'documento_visivel_{i}') == 'on'
                if arquivo:
                    DocumentoProjeto.objects.create(
                        projeto=projeto,
                        nome=nome,
                        arquivo=arquivo,
                        visivel_cliente=visivel
                    )
            messages.success(request, 'Projeto cadastrado com sucesso!')
            return redirect('crm:lista_projetos')
        else:
            messages.error(request, 'Erro ao cadastrar projeto. Verifique os campos.')
    else:
        form = ProjetoForm()
    return render(request, 'solar/cadastrar_projeto.html', {
        'form': form,
        'documentos_labels': documentos_labels
    })

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.change_projeto', raise_exception=True)
def editar_projeto(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk)
    documentos = projeto.documentos.all()
    documentos_labels = ['RG', 'CPF/CNPJ', 'Conta de Luz', 'Foto do Poste', 'Experiência']

    if request.method == 'POST':
        form = ProjetoForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto atualizado com sucesso!')
            return redirect('crm:detalhe_projeto', pk=projeto.pk)
        else:
            messages.error(request, 'Erro ao atualizar projeto. Verifique os campos.')
    else:
        form = ProjetoForm(instance=projeto)
    context = {
        'form': form,
        'projeto': projeto,
        'documentos': documentos,
        'documentos_labels': documentos_labels,
    }
    return render(request, 'solar/editar_projeto.html', context)

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.delete_projeto', raise_exception=True)
def excluir_projeto(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk)
    if request.method == 'POST':
        projeto.delete()
        messages.success(request, 'Projeto excluído com sucesso!')
        return redirect('crm:lista_projetos')
    return render(request, 'solar/confirmar_exclusao_projeto.html', {'projeto': projeto})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.add_etapa', raise_exception=True)
def cadastrar_etapa(request, pk):
    projeto = get_object_or_404(Projeto, pk=pk)

    if request.method == 'POST':
        form = EtapaForm(request.POST)
        if form.is_valid():
            etapa = form.save(commit=False)
            etapa.projeto = projeto
            etapa.save()
            messages.success(request, 'Etapa cadastrada com sucesso!')
            return redirect('crm:detalhe_projeto', pk=projeto.pk)
        else:
            messages.error(request, 'Erro ao cadastrar a etapa. Verifique os campos.')
            print("ERROS DO FORMULÁRIO:", form.errors)
    else:
        form = EtapaForm()

    return render(request, 'solar/cadastrar_etapa.html', {
        'form': form,
        'projeto': projeto
    })

# ------------------------------------------------------------------
# VIEWS DE MATERIAIS (CRM)
# ------------------------------------------------------------------
@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_material', raise_exception=True)
def lista_materiais(request):
    materiais = Material.objects.all()
    return render(request, 'solar/lista_materiais.html', {'materiais': materiais})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.add_material', raise_exception=True)
def cadastrar_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material cadastrado com sucesso!')
            return redirect('crm:lista_materiais')
        else:
            messages.error(request, 'Erro ao cadastrar material. Verifique os campos.')
    else:
        form = MaterialForm()
    return render(request, 'solar/cadastrar_material.html', {'form': form})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.change_material', raise_exception=True)
def editar_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material atualizado com sucesso!')
            return redirect('crm:lista_materiais')
        else:
            messages.error(request, 'Erro ao atualizar material. Verifique os campos.')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'solar/editar_material.html', {'form': form, 'material': material})

# ------------------------------------------------------------------
# VIEWS DE FORNECEDORES (CRM)
# ------------------------------------------------------------------
@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_fornecedor', raise_exception=True)
def lista_fornecedores(request):
    fornecedores = Fornecedor.objects.all()
    return render(request, 'solar/lista_fornecedores.html', {'fornecedores': fornecedores})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.add_fornecedor', raise_exception=True)
def cadastrar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('crm:lista_fornecedores')
        else:
            messages.error(request, 'Erro ao cadastrar fornecedor. Verifique os campos.')
    else:
        form = FornecedorForm()
    return render(request, 'solar/cadastrar_fornecedor.html', {'form': form})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.change_fornecedor', raise_exception=True)
def editar_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor atualizado com sucesso!')
            return redirect('crm:lista_fornecedores')
        else:
            messages.error(request, 'Erro ao atualizar fornecedor. Verifique os campos.')
    else:
        form = FornecedorForm(instance=fornecedor)
    return render(request, 'solar/editar_fornecedor.html', {'form': form, 'fornecedor': fornecedor})

# ------------------------------------------------------------------
# VIEWS DE FINANCEIRO (CRM)
# ------------------------------------------------------------------
@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_lancamentofinanceiro', raise_exception=True)
def lista_financeiro(request):
    lancamentos = LancamentoFinanceiro.objects.select_related('projeto').order_by('-data')
    return render(request, 'solar/lista_financeiro.html', {'lancamentos': lancamentos})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.add_lancamentofinanceiro', raise_exception=True)
def cadastrar_lancamento(request):
    if request.method == 'POST':
        form = LancamentoFinanceiroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lançamento registrado com sucesso!')
            return redirect('crm:lista_financeiro')
        else:
            messages.error(request, 'Erro ao registrar lançamento.')
    else:
        form = LancamentoFinanceiroForm()
    return render(request, 'solar/cadastrar_lancamento.html', {'form': form})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.view_lancamentofinanceiro', raise_exception=True)
def dashboard_financeiro(request):
    projetos = Projeto.objects.all()
    lancamentos = LancamentoFinanceiro.objects.select_related('projeto')

    projeto_id = request.GET.get('projeto')
    tipo = request.GET.get('tipo')
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if projeto_id:
        lancamentos = lancamentos.filter(projeto_id=projeto_id)
    if tipo:
        lancamentos = lancamentos.filter(tipo=tipo)
    if status:
        lancamentos = lancamentos.filter(status=status)
    if data_inicio:
        lancamentos = lancamentos.filter(data__gte=parse_date(data_inicio))
    if data_fim:
        lancamentos = lancamentos.filter(data__lte=parse_date(data_fim))

    resumo_tipos = lancamentos.values('tipo').annotate(total=Sum('valor'))
    tipo_labels = [r['tipo'].capitalize() for r in resumo_tipos]
    tipo_data = [float(r['total']) for r in resumo_tipos]

    resumo_projetos = lancamentos.values('projeto__nome').annotate(total=Sum('valor')).order_by('-total')
    projeto_labels = [r['projeto__nome'] for r in resumo_projetos]
    projeto_data = [float(r['total']) for r in resumo_projetos]

    context = {
        'tipo_labels': json.dumps(tipo_labels),
        'tipo_data': json.dumps(tipo_data),
        'projeto_labels': json.dumps(projeto_labels),
        'projeto_data': json.dumps(projeto_data),
        'projetos': projetos,
        'filtro': {
            'projeto': projeto_id,
            'tipo': tipo,
            'status': status,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
    }
    return render(request, 'solar/dashboard_financeiro.html', context)

# ------------------------------------------------------------------
# VIEWS DO PAINEL DO CLIENTE (E-COMMERCE)
# ------------------------------------------------------------------
def login_cliente(request):
    if request.user.is_authenticated:
        if request.user.is_customer:
            return redirect('crm:cliente_dashboard')
        else:
            messages.warning(request, "Você não tem acesso à área do cliente com esta conta. Por favor, faça login com uma conta de cliente.")
            logout(request)
            return redirect('login_ecommerce')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None and user.pode_acessar_ecommerce:
                login(request, user)
                messages.success(request, f"Bem-vindo(a) ao seu painel, {user.username}!")
                return redirect('crm:cliente_dashboard')
            else:
                messages.error(request, 'Credenciais inválidas ou você não tem acesso de cliente.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos corretamente!')
    
    return render(request, 'solar/cliente_login.html', {'form': AuthenticationForm(), 'titulo': 'Login Área do Cliente'})



@login_required
@user_passes_test(pode_acessar_ecommerce) # Garante que só quem pode acessar o e-commerce chegue aqui
def cliente_dashboard(request):
    """
    Dashboard unificado para o cliente, oferecendo acesso à loja e aos projetos.
    - Redireciona usuários staff/admin para o Dashboard CRM.
    - Verifica se o perfil de Cliente existe e, se não, redireciona para completá-lo.
    """
  
    if request.user.pode_acessar_crm:
        messages.info(request, "Você acessou a área do cliente. Redirecionando para o Dashboard CRM.")
        return redirect('crm:home')
    # --- FIM do NOVO: Redirecionamento para staff/admin ---

    cliente = None
    try:
        # Tenta obter o perfil do cliente associado ao usuário logado
        cliente = request.user.perfil_cliente
    except Cliente.DoesNotExist:
        # Se o perfil de Cliente não existe para este usuário, ele é None
        pass 

    # Se o perfil do cliente é None (não foi encontrado)
    if cliente is None:
        messages.warning(request, "Por favor, complete seu perfil de cliente para acessar todas as funcionalidades.")
        # Redireciona para a view de completar o perfil
        return redirect('crm:completar_perfil_cliente')

    # --- Lógica da Dashboard (executada APENAS se o perfil do cliente existe e não é staff/admin) ---
    # Somente mostra projetos se o perfil do cliente existe e o usuário é um cliente.
    projetos = Projeto.objects.filter(cliente=cliente).order_by('-data_inicio')
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em')

    cliente_tem_projetos = projetos.exists()
    cliente_tem_pedidos = pedidos.exists()

    projetos_data = []
    for projeto in projetos:
        etapas = projeto.etapas.order_by('data_inicio')
        etapas_concluidas = etapas.exclude(data_fim__isnull=True).count()
        total_etapas = etapas.count()

        percentual = 0
        if total_etapas > 0:
            percentual = round((etapas_concluidas / total_etapas) * 100, 2)

        lancamentos = LancamentoFinanceiro.objects.filter(projeto=projeto)
        pagos = lancamentos.filter(status='pago').aggregate(total=Sum('valor'))['total'] or 0
        pendentes = lancamentos.filter(status='pendente').aggregate(total=Sum('valor'))['total'] or 0

        projetos_data.append({
            'projeto': projeto,
            'etapas': etapas,
            'etapas_concluidas': etapas_concluidas,
            'total_etapas': total_etapas,
            'percentual': percentual,
            'pagos': pagos,
            'pendentes': pendentes,
        })

    # Contexto para o template
    context = {
        'cliente': cliente,
        'projetos_data': projetos_data,
        'pedidos': pedidos,
        'cliente_tem_projetos': cliente_tem_projetos,
        'cliente_tem_pedidos': cliente_tem_pedidos,
        'titulo': 'Meu Painel de Cliente',
    }
    return render(request, 'solar/cliente_dashboard.html', context)


# ------------------------------------------------------------------
# NOVA VIEW: Completar Perfil do Cliente
# ------------------------------------------------------------------
@login_required
@user_passes_test(pode_acessar_ecommerce)
def completar_perfil_cliente(request):
    """
    Permite ao usuário autenticado completar ou criar seu perfil de Cliente.
    """
    cliente_existente = None
    try:
        cliente_existente = request.user.perfil_cliente
    except Cliente.DoesNotExist:
        pass

    if cliente_existente and request.user.is_customer:
        messages.info(request, "Seu perfil de cliente já está completo.")
        return redirect('crm:cliente_dashboard')
    elif cliente_existente and not request.user.is_customer:
        messages.info(request, "Seu perfil de cliente já existe. Redirecionando para a loja.")
        return redirect('produtos:home')

    if request.method == 'POST':
        form = PerfilClienteForm(request.POST, instance=cliente_existente)
        if form.is_valid():
            try:
                with transaction.atomic():
                    cliente = form.save(commit=False)
                    cliente.usuario = request.user
                    cliente.save()

                    if not request.user.is_customer:
                        request.user.is_customer = True
                        request.user.save()

                    messages.success(request, "Seu perfil de cliente foi completado com sucesso! 🎉")
                    return redirect('crm:cliente_dashboard')
            except Exception as e:
                logger.error(f"Erro ao salvar perfil do cliente para {request.user.username}: {e}", exc_info=True)
                messages.error(request, f"Ocorreu um erro ao salvar seu perfil: {e}. Por favor, tente novamente.")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = PerfilClienteForm(instance=cliente_existente)
    
    context = {
        'form': form,
        'titulo': 'Complete Seu Perfil de Cliente',
        'cliente_existente': cliente_existente,
    }
    return render(request, 'solar/completar_perfil_cliente.html', context)


# ------------------------------------------------------------------
# VIEWS DE GERENCIAMENTO DE USUÁRIOS
# ------------------------------------------------------------------

@login_required
@user_passes_test(pode_acessar_crm)
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'solar/lista_usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(pode_acessar_crm)
def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_crm_staff = True
            user.save()
            messages.success(request, 'Usuário CRM cadastrado com sucesso!')
            return redirect('crm:lista_usuarios')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = UsuarioCreateForm()
    return render(request, 'solar/cadastrar_usuario.html', {'form': form})


@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.change_usuario', raise_exception=True)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('crm:lista_usuarios')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = UsuarioUpdateForm(instance=usuario)
    return render(request, 'solar/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.change_usuario', raise_exception=True)
def resetar_senha_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == "POST":
        form = SetPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Senha redefinida com sucesso!')
            return redirect('crm:lista_usuarios')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = SetPasswordForm(usuario)
    return render(request, "solar/resetar_senha_usuario.html", {"form": form, "usuario": usuario})

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('solar.delete_usuario', raise_exception=True)
def excluir_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
        return redirect('crm:lista_usuarios')
    return render(request, "solar/confirmar_excluir_usuario.html", {"usuario": usuario})

# ------------------------------------------------------------------
# VIEWS PARA GERENCIAMENTO DE PRODUTOS DO E-COMMERCE NO CRM
# ------------------------------------------------------------------
@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('produtos.view_produto', raise_exception=True)
def lista_produtos_ecommerce(request):
    produtos = Produto.objects.all().prefetch_related('images')
    context = {
        'produtos': produtos,
        'titulo': 'Gerenciar Produtos do E-commerce',
    }
    return render(request, 'solar/lista_produtos_ecommerce.html', context)

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('produtos.add_produto', raise_exception=True)
def adicionar_produto(request):
    if request.method == 'POST':
        form = ProdutoEcommerceForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                # Apenas salvamos o formulário. O modelo cuidará do slug.
                produto = form.save() # Podemos até remover o commit=False se não houver mais nada para adicionar

                # Lógica para salvar as imagens continua aqui
                for f in request.FILES.getlist('images'):
                    ProdutoImage.objects.create(produto=produto, image=f)

                messages.success(request, f'Produto "{produto.name}" adicionado com sucesso!')
                
                # A lógica de redirecionamento inteligente que já fizemos
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('crm:lista_produtos_ecommerce')
        else:
            messages.error(request, 'Erro ao adicionar produto. Verifique os campos.')
    else:
        form = ProdutoEcommerceForm(initial=request.GET.dict())
    
    # ... (o resto da sua view continua igual)
    # ...
    
    context = {
        'form': form,
        'titulo': 'Adicionar Novo Produto',
        'categorias': [
            'paineis_solares', 'inversores', 'baterias', 'kits_fotovoltaicos',
            'estruturas_montagem', 'acessorios', 'outros',
            'sistemas_backup', 'ferramentas_instalacao',
        ]
    }
    return render(request, 'solar/adiciona_produto.html', context)
   

@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('produtos.add_produto', raise_exception=True) # Permissão para ADICIONAR Produto
def adicionar_produto_ia(request):
    if request.method == 'POST':
        imagens = request.FILES.getlist('imagem_ia')
        if not imagens:
            messages.error(request, 'Nenhuma imagem foi enviada.')
            return redirect('crm:adicionar_produto_ia')

        sucessos = 0
        falhas = 0

        # Loop para processar e SALVAR cada imagem
        for imagem in imagens:
            try:
                # 1. Análise da Imagem
                dados_produto = analisar_imagem_produto(imagem)

                if 'error' in dados_produto:
                    print(f"Falha na IA para a imagem {imagem.name}: {dados_produto['error']}")
                    falhas += 1
                    continue

                # 2. Criação do Formulário com dados da IA
                form = ProdutoEcommerceForm(dados_produto)
                
                if form.is_valid():
                    with transaction.atomic():
                        # Salva o produto (o 'revisado=False' é automático se for o padrão do campo)
                        produto_novo = form.save() 
                        # Salva a imagem associada
                        ProdutoImage.objects.create(produto=produto_novo, image=imagem, is_main=True)
                        sucessos += 1
                else:
                    # Melhoria: Incluir a imagem na mensagem de erro para debug
                    print(f"Dados da IA inválidos para {imagem.name}: {form.errors.as_json()}") 
                    falhas += 1

            except Exception as e:
                # Melhoria: Capturar e logar o erro, e continuar o loop
                print(f"Erro inesperado ao processar {imagem.name}: {e}")
                falhas += 1

        # Mensagem de resumo final
        if sucessos > 0:
            messages.success(request, f'{sucessos} produto(s) foram criados e estão aguardando revisão.')
        if falhas > 0:
            messages.warning(request, f'{falhas} imagem(ns) não puderam ser processadas.')

        # Redireciona para a lista de produtos
        return redirect('crm:lista_produtos_ecommerce')

    return render(request, 'solar/adicionar_produto_ia.html')


@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('produtos.change_produto', raise_exception=True)
def editar_produto_ecommerce(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        # Instancia o formulário com os dados e arquivos do POST
        form = ProdutoEcommerceForm(request.POST, request.FILES, instance=produto)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    produto_salvo = form.save()
                    
                    # Lógica para adicionar novas imagens
                    novas_imagens = request.FILES.getlist('images')
                    if novas_imagens:
                        has_current_main_image = ProdutoImage.objects.filter(produto=produto_salvo, is_main=True).exists()

                        for i, f in enumerate(novas_imagens):
                            set_as_main = (i == 0 and not has_current_main_image)
                            ProdutoImage.objects.create(
                                produto=produto_salvo,
                                image=f,
                                is_main=set_as_main
                            )
                            if set_as_main:
                                has_current_main_image = True 
                    
                    messages.success(request, 'Produto e imagens atualizadas com sucesso! 🎉')

                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url) # Volta para a página de resultados
                    

                    return redirect('crm:editar_produto_ecommerce', produto_id=produto_salvo.id)
            
            except Exception as e:
                logger.error(f"Erro ao salvar produto/imagens: {e}", exc_info=True)
                messages.error(request, f'Erro ao salvar produto/imagens. Por favor, tente novamente.')
        else:
            # Se o formulário não for válido, as mensagens de erro serão exibidas
            messages.error(request, 'Houve um erro no formulário. Por favor, verifique os campos inválidos.')
            
    else:
        # Se for um GET, apenas renderiza o formulário
        form = ProdutoEcommerceForm(instance=produto)

    # Contexto para a renderização, tanto no GET quanto no POST (se houver erro)
    imagens_existentes = ProdutoImage.objects.filter(produto=produto).order_by('-is_main', 'id')
    context = {
        'form': form,
        'produto': produto,
        'titulo': f'Editar Produto: {produto.name}',
        'imagens_existentes': imagens_existentes,
    }
    return render(request, 'solar/editar_produto_ecommerce.html', context)


@login_required
@user_passes_test(pode_acessar_crm)
@permission_required('produtos.delete_produto', raise_exception=True)
def excluir_produto_ecommerce(request, produto_id):
    """
    Exclui um produto do e-commerce.
    """
    produto = get_object_or_404(Produto, id=produto_id) 

    if request.method == 'POST':
        produto.delete()
        messages.success(request, f'Produto "{produto.name}" excluído com sucesso!')
        return redirect('crm:lista_produtos_ecommerce')
    
    context = {
        'produto': produto,
        'titulo': f'Confirmar Exclusão: {produto.name}',
    }
    return render(request, 'solar/confirmar_exclusao_produto_ecommerce.html', context)


# crm/views.py
...
@login_required
@user_passes_test(pode_acessar_crm)
def excluir_imagem_produto(request, imagem_id):
    imagem = get_object_or_404(ProdutoImage, id=imagem_id)
    produto = imagem.produto

    if request.method == "POST":
        try:
            if produto.images.count() <= 1:
                messages.error(request, "O produto deve ter pelo menos uma imagem cadastrada.")
            else:
                # O parâmetro save=False é opcional aqui, mas é uma boa prática
                imagem.image.delete(save=False)
                imagem.delete()
                messages.success(request, "Imagem excluída com sucesso!")
        except Exception as e:
            logger.error(f"Erro na exclusão da imagem {imagem_id} do produto {produto.id}: {e}", exc_info=True)
            messages.error(request, f"Erro ao excluir imagem: {e}. Verifique os logs do servidor.")
        
        # Corrija o nome da rota de redirecionamento aqui
        return redirect("crm:editar_produto_ecommerce", produto_id=produto.id)

    # se chegar aqui (GET), apenas redireciona de volta
    return redirect("crm:editar_produto_ecommerce", produto_id=produto.id)




def acesso_negado(request):
    return render(request, 'solar/acesso_negado.html', status=403)

@login_required
@user_passes_test(pode_acessar_crm)
def selecionar_metodo_criacao(request):
 
    return render(request, 'solar/selecionar_metodo_criacao.html')


# Em solar/views.py

@login_required
@user_passes_test(pode_acessar_crm)
def lista_produtos_para_revisao(request):
    """
    Lista apenas os produtos que foram criados pela IA e ainda
    não foram revisados por um humano.
    """
    # Filtramos o modelo Produto para pegar apenas os com revisado=False
    produtos_para_revisar = Produto.objects.filter(revisado=False).order_by('-created_at')
    
    context = {
        'produtos': produtos_para_revisar,
    }
    return render(request, 'solar/lista_produtos_para_revisao.html', context)