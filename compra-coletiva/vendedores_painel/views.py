# vendedores_painel/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify # Para gerar slugs
from django.db import transaction # Para garantir atomicidade
import uuid # Para IDs únicos se necessário

from ofertas.models import Oferta # Importe Oferta
from ofertas.forms import OfertaForm # Importe OfertaForm

# Decorador para garantir que apenas usuários associados a vendedores acessem o painel
def vendedor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.eh_vendedor_ou_associado:
            messages.error(request, 'Você não tem permissão para acessar o painel do vendedor.')
            return redirect('ofertas:lista_ofertas')
        return view_func(request, *args, **kwargs)
    return wrapper

@vendedor_required # Aplica o novo decorador
def dashboard_vendedor(request):
    vendedor_associado = request.user.vendedor
    ofertas_do_vendedor = Oferta.objects.filter(vendedor=vendedor_associado).order_by('-data_criacao')

    contexto = {
        'vendedor': vendedor_associado,
        'ofertas': ofertas_do_vendedor,
        'titulo_pagina': f'Painel do Vendedor: {vendedor_associado.nome_empresa}'
    }
    return render(request, 'vendedores_painel/dashboard.html', contexto)

@vendedor_required
def listar_cupons_vendedor(request):
    vendedor_associado = request.user.vendedor
    # Busca todos os cupons de TODAS as ofertas deste vendedor
    cupons = Cupom.objects.filter(oferta__vendedor=vendedor_associado).order_by('-data_geracao')

    contexto = {
        'cupons': cupons,
        'titulo_pagina': f'Cupons Gerados para {vendedor_associado.nome_empresa}'
    }
    return render(request, 'vendedores_painel/listar_cupons.html', contexto)

@vendedor_required
def resgatar_cupom(request, codigo_cupom):
    # Tenta encontrar o cupom e garantir que ele pertença a uma oferta do vendedor logado
    cupom = get_object_or_404(
        Cupom, 
        codigo=codigo_cupom, 
        oferta__vendedor=request.user.vendedor # Garante que o cupom é do vendedor logado
    )

    if request.method == 'POST':
        if not cupom.esta_valido:
            messages.error(request, f'O cupom {cupom.codigo} não pode ser resgatado. Status atual: {cupom.get_status_display()}.')
            return redirect('vendedores_painel:listar_cupons_vendedor')
        
        try:
            with transaction.atomic():
                cupom.status = 'resgatado'
                cupom.data_resgate = timezone.now()
                cupom.resgatado_por = request.user # Registra quem resgatou o cupom
                cupom.save()
                messages.success(request, f'Cupom {cupom.codigo} resgatado com sucesso para "{cupom.oferta.titulo}"!')
                return redirect('vendedores_painel:listar_cupons_vendedor')
        except Exception as e:
            messages.error(request, f'Erro ao resgatar cupom {cupom.codigo}: {e}.')
            return redirect('vendedores_painel:listar_cupons_vendedor')
    
    # Se for GET, exibe a página de confirmação de resgate
    contexto = {
        'cupom': cupom,
        'titulo_pagina': f'Resgatar Cupom: {cupom.codigo}'
    }
    return render(request, 'vendedores_painel/confirmar_resgate_cupom.html', contexto)

# Opcional: Uma view para buscar um cupom pelo código para resgate rápido
@vendedor_required
def buscar_cupom_para_resgate(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo_cupom')
        if codigo:
            return redirect('vendedores_painel:resgatar_cupom', codigo_cupom=codigo)
        else:
            messages.error(request, 'Por favor, insira um código de cupom.')
    
    contexto = {
        'titulo_pagina': 'Buscar Cupom para Resgate'
    }
    return render(request, 'vendedores_painel/buscar_cupom.html', contexto)


@vendedor_required
def criar_oferta(request):
    if request.method == 'POST':
        form = OfertaForm(request.POST, request.FILES) # request.FILES é para upload de imagem
        if form.is_valid():
            with transaction.atomic():
                oferta = form.save(commit=False) # Não salva ainda, apenas cria o objeto
                oferta.vendedor = request.user.vendedor # Associa a oferta ao vendedor logado
                oferta.slug = slugify(oferta.titulo) # Gera o slug a partir do título
                
                # Garante unicidade do slug se já existir
                original_slug = oferta.slug
                num = 1
                while Oferta.objects.filter(slug=oferta.slug).exists():
                    oferta.slug = f"{original_slug}-{num}"
                    num += 1

                # Define status e publicada iniciais (pode ser 'pendente' e False para moderação)
                oferta.status = 'pendente' 
                oferta.publicada = False # Administrador revisa e publica
                oferta.save()

                messages.success(request, 'Oferta criada com sucesso! Ela passará por moderação antes de ser publicada.')
                return redirect('vendedores_painel:dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = OfertaForm() # Formulário vazio para requisições GET
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Criar Nova Oferta'
    }
    return render(request, 'vendedores_painel/criar_editar_oferta.html', contexto)

@vendedor_required
def editar_oferta(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk, vendedor=request.user.vendedor) # Garante que só edite suas próprias ofertas

    if request.method == 'POST':
        # Instancia o formulário com os dados da requisição e a instância da oferta
        # request.FILES é importante para lidar com uploads de imagem
        form = OfertaForm(request.POST, request.FILES, instance=oferta) 
        if form.is_valid():
            with transaction.atomic():
                oferta = form.save(commit=False)
                # O slug só é atualizado se o título mudar e for diferente do original
                # ou se o slug já existir e precisar de um novo
                if 'titulo' in form.changed_data or Oferta.objects.filter(slug=oferta.slug).exclude(pk=oferta.pk).exists():
                    oferta.slug = slugify(oferta.titulo)
                    original_slug = oferta.slug
                    num = 1
                    while Oferta.objects.filter(slug=oferta.slug).exclude(pk=oferta.pk).exists():
                        oferta.slug = f"{original_slug}-{num}"
                        num += 1

                # Reverter status para pendente e não publicada se houver edição significativa?
                # Depende da sua regra de negócio. Por agora, não alteramos o status/publicação aqui.
                # Se quiser moderação após cada edição, adicione:
                # oferta.status = 'pendente'
                # oferta.publicada = False

                oferta.save()

                messages.success(request, f'Oferta "{oferta.titulo}" atualizada com sucesso!')
                return redirect('vendedores_painel:dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # Preenche o formulário com os dados da oferta existente para requisições GET
        form = OfertaForm(instance=oferta) 
    
    contexto = {
        'form': form,
        'oferta': oferta, # Passa a oferta para o template, útil para o título da página
        'titulo_pagina': f'Editar Oferta: {oferta.titulo}'
    }
    return render(request, 'vendedores_painel/criar_editar_oferta.html', contexto)