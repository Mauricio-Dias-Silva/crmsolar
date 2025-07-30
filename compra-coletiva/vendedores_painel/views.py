# vendedores_painel/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Sum, Count

# Importe modelos e formulários dos apps relacionados
from ofertas.models import Oferta, Vendedor
from ofertas.forms import OfertaForm
from compras.models import Cupom, Compra
from pedidos_coletivos.models import CreditoUsuario, PedidoColetivo
from contas.models import Usuario


# Decorador para garantir que apenas usuários associados a vendedores APROVADOS acessem o painel
def vendedor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Você precisa estar logado para acessar esta área.')
            return redirect('account_login')
        
        if not request.user.vendedor or \
           request.user.vendedor.status_aprovacao != 'aprovado':
            
            if request.user.vendedor and request.user.vendedor.status_aprovacao == 'pendente':
                messages.warning(request, 'Seu cadastro de vendedor está pendente de aprovação. Por favor, aguarde a análise.')
            elif request.user.vendedor and request.user.vendedor.status_aprovacao == 'suspenso':
                messages.error(request, 'Sua conta de vendedor está suspensa. Entre em contato com o suporte.')
            elif request.user.vendedor and request.user.vendedor.status_aprovacao == 'rejeitado':
                messages.error(request, 'Seu cadastro de vendedor foi rejeitado. Entre em contato com o suporte para mais informações.')
            else:
                 messages.error(request, 'Você não tem permissão para acessar o painel do vendedor. Cadastre sua empresa ou associe-se a um vendedor aprovado.')
            
            return redirect('ofertas:lista_ofertas')
        return view_func(request, *args, **kwargs)
    return wrapper

@vendedor_required
def dashboard_vendedor(request):
    vendedor_associado = request.user.vendedor
    ofertas_do_vendedor = Oferta.objects.filter(vendedor=vendedor_associado).order_by('-data_criacao')

    # --- Relatórios para o Vendedor ---
    total_cupons_vendidos = Cupom.objects.filter(
    Q(oferta__vendedor=vendedor_associado) & ( # <--- Q object é posicional
        Q(compra__status_pagamento='aprovada') |
        Q(pedido_coletivo__status_pagamento='aprovado_mp', pedido_coletivo__status_lote='concretizado')
    )
).count()


    total_cupons_resgatados = Cupom.objects.filter(
        oferta__vendedor=vendedor_associado,
        status='resgatado'
    ).count()

    receita_bruta_compras_unidade = Compra.objects.filter(
        oferta__vendedor=vendedor_associado,
        status_pagamento='aprovada'
    ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0.00

    receita_bruta_pedidos_coletivos = PedidoColetivo.objects.filter(
        oferta__vendedor=vendedor_associado,
        status_pagamento='aprovado_mp',
        status_lote='concretizado'
    ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0.00
    
    receita_bruta_total = receita_bruta_compras_unidade + receita_bruta_pedidos_coletivos

    contexto = {
        'vendedor': vendedor_associado,
        'ofertas': ofertas_do_vendedor,
        'titulo_pagina': f'Painel do Vendedor: {vendedor_associado.nome_empresa}',
        'total_cupons_vendidos': total_cupons_vendidos,
        'total_cupons_resgatados': total_cupons_resgatados,
        'receita_bruta': receita_bruta_total,
    }
    return render(request, 'vendedores_painel/dashboard.html', contexto)

@vendedor_required
def criar_oferta(request): # <-- FUNÇÃO RESTAURADA
    if request.method == 'POST':
        form = OfertaForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                oferta = form.save(commit=False)
                oferta.vendedor = request.user.vendedor
                oferta.slug = slugify(oferta.titulo)
                
                original_slug = oferta.slug
                num = 1
                while Oferta.objects.filter(slug=oferta.slug).exists():
                    oferta.slug = f"{original_slug}-{num}"
                    num += 1

                oferta.status = 'pendente'
                oferta.publicada = False
                oferta.save()

                messages.success(request, 'Oferta criada com sucesso! Ela passará por moderação antes de ser publicada.')
                return redirect('vendedores_painel:dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = OfertaForm()
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Criar Nova Oferta'
    }
    return render(request, 'vendedores_painel/criar_editar_oferta.html', contexto)

@vendedor_required
def editar_oferta(request, pk): # <-- FUNÇÃO RESTAURADA
    oferta = get_object_or_404(Oferta, pk=pk, vendedor=request.user.vendedor)

    if request.method == 'POST':
        form = OfertaForm(request.POST, request.FILES, instance=oferta)
        if form.is_valid():
            with transaction.atomic():
                oferta = form.save(commit=False)
                if 'titulo' in form.changed_data or Oferta.objects.filter(slug=oferta.slug).exclude(pk=oferta.pk).exists():
                    oferta.slug = slugify(oferta.titulo)
                    original_slug = oferta.slug
                    num = 1
                    while Oferta.objects.filter(slug=oferta.slug).exclude(pk=oferta.pk).exists():
                        oferta.slug = f"{original_slug}-{num}"
                        num += 1

                oferta.save()

                messages.success(request, f'Oferta "{oferta.titulo}" atualizada com sucesso!')
                return redirect('vendedores_painel:dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = OfertaForm(instance=oferta)
    
    contexto = {
        'form': form,
        'oferta': oferta,
        'titulo_pagina': f'Editar Oferta: {oferta.titulo}'
    }
    return render(request, 'vendedores_painel/criar_editar_oferta.html', contexto)

@vendedor_required
def gerenciar_cupons(request): # Renomeada de listar_cupons_vendedor
    vendedor = request.user.vendedor
    
    # CORREÇÃO AQUI: A query do filter() para cupons
    # Garante que as condições de Q estão corretamente passadas como argumentos posicionais
    cupons_queryset = Cupom.objects.filter(
    Q(oferta__vendedor=vendedor) & (
        Q(compra__isnull=False, compra__status_pagamento='aprovada') |
        Q(pedido_coletivo__isnull=False, pedido_coletivo__status_pagamento='aprovado_mp', pedido_coletivo__status_lote='concretizado')
    )
).select_related('oferta', 'usuario', 'compra', 'pedido_coletivo').order_by('-data_criacao')


    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'todos':
        cupons_queryset = cupons_queryset.filter(status=status_filter)

    query = request.GET.get('q')
    if query:
        cupons_queryset = cupons_queryset.filter(
            Q(codigo__icontains=query) |
            Q(usuario__username__icontains=query) |
            Q(usuario__email__icontains=query)
        ).distinct()

    paginator = Paginator(cupons_queryset, 10)
    page = request.GET.get('page')
    try:
        cupons = paginator.page(page)
    except PageNotAnInteger:
        cupons = paginator.page(1)
    except EmptyPage:
        cupons = paginator.page(paginator.num_pages)

    contexto = {
        'cupons': cupons,
        'titulo_pagina': 'Gerenciar Cupons',
        'current_status_filter': status_filter,
        'search_query': query,
        'cupom_status_choices': Cupom.STATUS_CHOICES
    }
    return render(request, 'vendedores_painel/gerenciar_cupons.html', contexto)


@vendedor_required
def resgatar_cupom(request, cupom_id):
    cupom = get_object_or_404(Cupom, id=cupom_id, oferta__vendedor=request.user.vendedor)

    if request.method == 'POST':
        if cupom.status == 'disponivel':
            cupom.status = 'resgatado'
            cupom.data_resgate = timezone.now()
            cupom.resgatado_por = request.user
            cupom.save()
            messages.success(request, f'Cupom "{cupom.codigo}" resgatado com sucesso!')
        else:
            messages.warning(request, f'O cupom "{cupom.codigo}" já foi resgatado ou não está disponível.')
        return redirect('vendedores_painel:gerenciar_cupons')
    
    contexto = {
        'cupom': cupom,
        'titulo_pagina': 'Confirmar Resgate de Cupom'
    }
    return render(request, 'vendedores_painel/confirmar_resgate_cupom.html', contexto)


@vendedor_required
def buscar_cupom_para_resgate(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo_cupom')
        if codigo:
            cupom = get_object_or_404(Cupom, codigo=codigo, oferta__vendedor=request.user.vendedor)
            return redirect('vendedores_painel:resgatar_cupom', cupom_id=cupom.id)
        else:
            messages.error(request, 'Por favor, insira um código de cupom.')
    
    contexto = {
        'titulo_pagina': 'Buscar Cupom para Resgate'
    }
    return render(request, 'vendedores_painel/buscar_cupom.html', contexto)