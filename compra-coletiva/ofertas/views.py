# ofertas/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Oferta, Categoria, Avaliacao, Banner, Vendedor
from .forms import AvaliacaoForm
from compras.models import Cupom



# --- FUNÇÃO AUXILIAR: PARA REDUZIR DUPLICAÇÃO DE CÓDIGO ---
def _get_ofertas_filtradas_paginadas(request, ofertas_queryset, categoria_selecionada, apenas_lote_flag):
    """
    Função auxiliar para aplicar busca, ordenação e paginação.
    Retorna as ofertas paginadas e os parâmetros de filtro/ordenação.
    """
    query = request.GET.get('q')
    if query:
        ofertas_queryset = ofertas_queryset.filter(
            Q(titulo__icontains=query) |
            Q(descricao_detalhada__icontains=query) |
            Q(vendedor__nome_empresa__icontains=query)
        )

    ordenar_por = request.GET.get('ordenar_por', '-data_inicio')
    opcoes_ordenacao = {
        'recentes': '-data_inicio',
        'antigas': 'data_inicio',
        'menor_preco': 'preco_desconto',
        'maior_preco': '-preco_desconto',
        'mais_vendidos': '-quantidade_vendida',
    }
    if ordenar_por in opcoes_ordenacao:
        ofertas_queryset = ofertas_queryset.order_by(opcoes_ordenacao[ordenar_por])
    else:
        ordenar_por = '-data_inicio'
        ofertas_queryset = ofertas_queryset.order_by(ordenar_por)

    items_por_pagina = 9
    paginator = Paginator(ofertas_queryset, items_por_pagina)
    page_number = request.GET.get('page')

    try:
        ofertas_paginadas = paginator.page(page_number)
    except PageNotAnInteger:
        ofertas_paginadas = paginator.page(1)
    except EmptyPage:
        ofertas_paginadas = paginator.page(paginator.num_pages)

    return ofertas_paginadas, query, ordenar_por


# --- NOVA VIEW PARA 'COMPRE JUNTO!' ---
def compre_junto_view(request, slug_categoria=None):
    ofertas_base = Oferta.objects.filter(
        publicada=True,
        status__in=['ativa', 'sucesso'],
        data_termino__gte=timezone.now(),
        vendedor__status_aprovacao='aprovado', # Filtro do vendedor
        tipo_oferta='lote' # <--- CORREÇÃO AQUI: DENTRO DO .filter()
    )

    categoria_selecionada = None
    if slug_categoria:
        categoria_selecionada = get_object_or_404(Categoria, slug=slug_categoria)
        ofertas_base = ofertas_base.filter(categoria=categoria_selecionada)

    ofertas_paginadas, query, ordenar_por = _get_ofertas_filtradas_paginadas(
        request, ofertas_base, categoria_selecionada, True # Passa True para apenas_lote_flag
    )

    categorias = Categoria.objects.all().order_by('nome')

    contexto = {
        'ofertas': ofertas_paginadas,
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
        'query_busca': query,
        'ordenar_por_selecionado': ordenar_por,
        'titulo_pagina': 'Compre Junto: Ofertas Coletivas!',
        'apenas_lote': True,
    }
    return render(request, 'ofertas/lista_ofertas_coletivas.html', contexto)


# --- VIEW ORIGINAL 'lista_ofertas' (SIMPLIFICADA) ---
def lista_ofertas(request, slug_categoria=None):
    ofertas_base = Oferta.objects.filter(
        publicada=True,
        status__in=['ativa', 'sucesso'],
        data_termino__gte=timezone.now(),
        tipo_oferta='unidade', # <--- CORREÇÃO AQUI: DENTRO DO .filter()
        vendedor__status_aprovacao='aprovado' # <--- FILTRO DO VENDEDOR APROVADO AQUI
    )

    categoria_selecionada = None
    if slug_categoria:
        categoria_selecionada = get_object_or_404(Categoria, slug=slug_categoria)
        ofertas_base = ofertas_base.filter(categoria=categoria_selecionada)

    ofertas_paginadas, query, ordenar_por = _get_ofertas_filtradas_paginadas(
        request, ofertas_base, categoria_selecionada, False
    )

    # Lógica FINAL para renderizar a HOMEPAGE ou a LISTA GERAL
    if not slug_categoria and not query:
        ofertas_destaque = Oferta.objects.filter(
            publicada=True,
            status__in=['ativa', 'sucesso'],
            data_termino__gte=timezone.now(),
            destaque=True,
            tipo_oferta='unidade',
            vendedor__status_aprovacao='aprovado' # <--- FILTRO DO VENDEDOR APROVADO AQUI
        ).order_by('-data_inicio')[:4]

        ofertas_ativas_paginadas = ofertas_base.exclude(destaque=True)
        template_para_renderizar = 'ofertas/home.html'
        titulo_pagina_final = 'Bem-vindo ao VarejoUnido!'
        
        banners = Banner.objects.filter(ativo=True).order_by('ordem')
        vendedores_destaque = Vendedor.objects.filter(ativo=True).order_by('?')[:4]
    else:
        ofertas_destaque = None
        ofertas_paginadas_home = None # Não usado
        template_para_renderizar = 'ofertas/lista_ofertas.html'
        banners = None
        vendedores_destaque = None
        titulo_pagina_final = 'Todas as Ofertas'
        if categoria_selecionada:
            titulo_pagina_final = f'Ofertas em {categoria_selecionada.nome}'
        elif query:
            titulo_pagina_final = f'Resultados da Busca para "{query}"'


    categorias = Categoria.objects.all().order_by('nome')

    contexto = {
        'ofertas': ofertas_paginadas if template_para_renderizar != 'ofertas/home.html' else ofertas_paginadas, # Usar ofertas_paginadas para ambas as branches da home
        'ofertas_destaque': ofertas_destaque,
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
        'query_busca': query,
        'ordenar_por_selecionado': ordenar_por,
        'titulo_pagina': titulo_pagina_final,
        'apenas_lote': False, # Sempre False para esta view
        'banners': banners,
        'vendedores_destaque': vendedores_destaque,
    }
    return render(request, template_para_renderizar, contexto)


# ofertas/views.py (apenas a função detalhe_oferta)

# ... (imports existentes) ...

@login_required 
def detalhe_oferta(request, slug_oferta):
    oferta = get_object_or_404(Oferta, slug=slug_oferta)
    
    avaliacoes = Avaliacao.objects.filter(oferta=oferta).order_by('-data_avaliacao')
    
    media_avaliacoes = avaliacoes.aggregate(Avg('nota'))['nota__avg']
    if media_avaliacoes:
        media_avaliacoes = round(media_avaliacoes, 1)
    
    avaliacao_existente = None
    if request.user.is_authenticated:
        avaliacao_existente = Avaliacao.objects.filter(oferta=oferta, usuario=request.user).first()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Você precisa estar logado para enviar uma avaliação.")
            return redirect('account_login')
        
        if avaliacao_existente:
            messages.warning(request, "Você já avaliou esta oferta. Sua avaliação foi atualizada.")
            form_avaliacao = AvaliacaoForm(request.POST, instance=avaliacao_existente)
        else:
            form_avaliacao = AvaliacaoForm(request.POST)
        
        if form_avaliacao.is_valid():
            avaliacao = form_avaliacao.save(commit=False)
            avaliacao.oferta = oferta
            avaliacao.usuario = request.user
            avaliacao.save()
            messages.success(request, "Sua avaliação foi enviada com sucesso!")
            return redirect('ofertas:detalhe_oferta', slug_oferta=oferta.slug)
        else:
            messages.error(request, "Por favor, corrija os erros na sua avaliação.")
    else:
        form_avaliacao = AvaliacaoForm(instance=avaliacao_existente)

    cupom_usuario = None
    if request.user.is_authenticated:
        cupom_usuario = Cupom.objects.filter(
            usuario=request.user, 
            oferta=oferta, 
            status__in=['disponivel', 'resgatado']
        ).first()

    contexto = {
        'oferta': oferta,
        'cupom_usuario': cupom_usuario,
        'avaliacoes': avaliacoes,
        'media_avaliacoes': media_avaliacoes,
        'form_avaliacao': form_avaliacao,
        'avaliacao_existente': avaliacao_existente,
        'titulo_pagina': oferta.titulo, # Mantém o título da aba do navegador
        # --- NOVAS VARIÁVEIS PARA SEO ---
        'seo_description': oferta.descricao_detalhada[:160], # Pega os primeiros 160 caracteres
        'seo_keywords': f"{oferta.titulo}, {oferta.categoria.nome}, {oferta.vendedor.nome_empresa}, varejounido, oferta, desconto",
        'og_title': oferta.titulo,
        'og_description': oferta.descricao_detalhada[:160],
        'og_image': oferta.imagem_principal.url if oferta.imagem_principal else '', # URL da imagem da oferta
        'og_type': 'product', # Ou 'website'
    }
    return render(request, 'ofertas/detalhe_oferta.html', contexto)