
# ofertas/views.py (apenas o trecho da função detalhe_oferta)

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg # Importe Avg para calcular a média das notas
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.contrib import messages # Para mensagens de sucesso/erro
from django.contrib.auth.decorators import login_required # Para exigir login ao avaliar

from .models import Oferta, Categoria, Avaliacao # Importe Avaliacao
from .forms import AvaliacaoForm # Importe AvaliacaoForm
from compras.models import Cupom 


# ... (lista_ofertas - permanece a mesma) ...

def lista_ofertas(request, slug_categoria=None):
    # 1. Filtro base de ofertas: ativas, publicadas e não expiradas
    ofertas_base = Oferta.objects.filter(
        publicada=True,
        status__in=['ativa', 'sucesso'],
        data_termino__gte=timezone.now()
    )

    # 2. Lógica de Filtro por Categoria
    categoria_selecionada = None
    if slug_categoria:
        categoria_selecionada = get_object_or_404(Categoria, slug=slug_categoria)
        ofertas_base = ofertas_base.filter(categoria=categoria_selecionada)

    # 3. Lógica de Busca por termo (query parameter 'q')
    query = request.GET.get('q')
    if query:
        ofertas_base = ofertas_base.filter(
            Q(titulo__icontains=query) |
            Q(descricao_detalhada__icontains=query) |
            Q(vendedor__nome_empresa__icontains=query)
        )

    # 4. Lógica de Ordenação (query parameter 'ordenar_por')
    # O padrão é '-data_inicio' (mais recentes)
    ordenar_por = request.GET.get('ordenar_por', '-data_inicio')

    opcoes_ordenacao = {
        'recentes': '-data_inicio',
        'antigas': 'data_inicio',
        'menor_preco': 'preco_desconto',
        'maior_preco': '-preco_desconto',
        'mais_vendidos': '-quantidade_vendida',
    }

    if ordenar_por in opcoes_ordenacao:
        ofertas_base = ofertas_base.order_by(opcoes_ordenacao[ordenar_por])
    else:
        # Se o parâmetro for inválido, volta para a ordenação padrão
        ordenar_por = '-data_inicio'
        ofertas_base = ofertas_base.order_by(ordenar_por)


    # 5. Lógica para a Página Inicial (home.html) vs. Listas de Categoria/Busca
    if not slug_categoria and not query: # Se não há categoria ou busca, é a página inicial pura
        ofertas_destaque = Oferta.objects.filter(
            publicada=True,
            status__in=['ativa', 'sucesso'],
            data_termino__gte=timezone.now(),
            destaque=True
        ).order_by('-data_inicio')[:4] # Limita a 4 ofertas em destaque

        # Exclui ofertas em destaque da lista principal para não duplicar na home
        ofertas_ativas_paginadas = ofertas_base.exclude(destaque=True)
        template_name = 'ofertas/home.html'
        titulo_pagina = 'Bem-vindo ao Nosso Site de Ofertas!'
    else: # Para listas filtradas/buscadas ou categorias específicas
        ofertas_destaque = None # Não exibe destaques nessas páginas
        ofertas_ativas_paginadas = ofertas_base # Usa a lista base para paginação
        template_name = 'ofertas/lista_ofertas.html'
        titulo_pagina = 'Todas as Ofertas'
        if categoria_selecionada:
            titulo_pagina = f'Ofertas em {categoria_selecionada.nome}'
        elif query:
            titulo_pagina = f'Resultados da Busca para "{query}"'


    # 6. Paginação (Aplicada à lista de ofertas ativas/paginadas)
    items_por_pagina = 9 # Define quantos itens aparecerão por página
    paginator = Paginator(ofertas_ativas_paginadas, items_por_pagina)
    page_number = request.GET.get('page') # Pega o número da página da URL (ex: ?page=2)

    try:
        ofertas_paginadas = paginator.page(page_number)
    except PageNotAnInteger:
        # Se o parâmetro de página não for um inteiro, entrega a primeira página.
        ofertas_paginadas = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do intervalo (ex: 9999), entrega a última página de resultados.
        ofertas_paginadas = paginator.page(paginator.num_pages)


    # 7. Contexto e Renderização
    categorias = Categoria.objects.all().order_by('nome') # Todas as categorias para o menu

    contexto = {
        'ofertas': ofertas_paginadas, # Agora passamos as ofertas já paginadas
        'ofertas_destaque': ofertas_destaque, # Apenas para home.html
        'categorias': categorias,
        'categoria_selecionada': categoria_selecionada,
        'query_busca': query,
        'ordenar_por_selecionado': ordenar_por, # Passa o critério de ordenação selecionado
        'titulo_pagina': titulo_pagina,
    }
    return render(request, template_name, contexto)



@login_required # Garante que apenas usuários logados possam acessar esta view
def detalhe_oferta(request, slug_oferta):
    oferta = get_object_or_404(Oferta, slug=slug_oferta)
    
    # Obter todas as avaliações para esta oferta
    avaliacoes = Avaliacao.objects.filter(oferta=oferta).order_by('-data_avaliacao')
    
    # Calcular a média das notas (se houver avaliações)
    media_avaliacoes = avaliacoes.aggregate(Avg('nota'))['nota__avg']
    if media_avaliacoes:
        media_avaliacoes = round(media_avaliacoes, 1) # Arredonda para uma casa decimal
    
    # Verificar se o usuário logado já avaliou esta oferta
    avaliacao_existente = None
    if request.user.is_authenticated:
        avaliacao_existente = Avaliacao.objects.filter(oferta=oferta, usuario=request.user).first()
    
    # Lógica para o formulário de avaliação
    if request.method == 'POST':
        if not request.user.is_authenticated: # Dupla checagem, já que a view é @login_required
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
        # Se for GET, inicializa o formulário. Se já avaliou, pré-preenche com a avaliação existente.
        form_avaliacao = AvaliacaoForm(instance=avaliacao_existente)

    # Lógica para cupons (já existente)
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
        'avaliacao_existente': avaliacao_existente, # Para controle no template
        'titulo_pagina': oferta.titulo,
    }
    return render(request, 'ofertas/detalhe_oferta.html', contexto)