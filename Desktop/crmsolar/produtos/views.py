# produtos/views.py
from decimal import Decimal, InvalidOperation
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import CarouselImage, Pedido, Item, Produto, ProdutoImage, RegiaoFrete
from .forms import CustomRegisterForm
from solar.models import Proposta,ProjetoExecutado 

try:
    from solar.models import Cliente
except Exception:
    Cliente = None

from django.contrib.auth import get_user_model
User = get_user_model()


# --------------------------
# PÁGINAS PRINCIPAIS
# --------------------------
def home(request):
    """
    Função Principal do Site (Antiga Home).
    Renderiza a nova home_page.html com destaque de produtos, carrossel e portfólio.
    """
    
    # --- 1. CONFIGURAÇÃO DE CATEGORIAS (Para o Navbar e Rodapé) ---
    categorias_esperadas = [
        'paineis_solares', 'inversores', 'baterias', 'kits_fotovoltaicos',
        'estruturas_montagem', 'acessorios', 'outros',
        'sistemas_backup', 'ferramentas_instalacao',
    ]
    categorias_para_template = [
        {'nome_url': cat, 'nome_exibicao': cat.replace('_', ' ').title()}
        for cat in categorias_esperadas
    ]

    # --- 2. CARROSSEL / BANNERS ---
    carousel_images = []
    try:
        carousel_images = CarouselImage.objects.filter(is_active=True)
    except Exception:
        pass

    # --- 3. PRODUTOS EM DESTAQUE (Unificação) ---
    # Tenta buscar 8 produtos ativos, que é o que o template home_page.html espera.
    produtos_em_destaque = Produto.objects.filter(is_active=True).order_by('-created_at')[:8]

    # Se a lista estiver vazia, busca qualquer produto recente para preencher
    if not produtos_em_destaque.exists():
        produtos_em_destaque = Produto.objects.all().order_by('-created_at')[:8]

    # --- 4. PROJETOS PARA O PORTFÓLIO (Seção de Credibilidade) ---
    try:
        # Garante a importação do modelo, se ele estiver no app 'solar'
        from solar.models import ProjetoExecutado 
        projetos_em_destaque = ProjetoExecutado.objects.filter(is_active=True).order_by('-potencia_kwp')[:4]
    except Exception:
        projetos_em_destaque = [] 

    context = {
        'produtos_em_destaque': produtos_em_destaque, # NOVO NOME ESPERADO PELO TEMPLATE
        'carousel_images': carousel_images,
        'categorias_ativas': categorias_para_template, # Essencial para o Navbar e Rodapé
        'projetos_em_destaque': projetos_em_destaque,
    }
    
    # Renderiza o novo template de entrada
    return render(request, 'produtos/home.html', context)

def produtos_por_categoria(request, categoria_slug):
    categorias_validas = [
        'paineis_solares', 'inversores', 'baterias', 'kits_fotovoltaicos',
        'estruturas_montagem', 'acessorios', 'outros',
        'sistemas_backup', 'ferramentas_instalacao',
    ]

    if categoria_slug not in categorias_validas:
        messages.error(request, "Categoria inválida.")
        return redirect('produtos:home')

    produtos_da_categoria = Produto.objects.filter(categoria_id=categoria_slug, is_active=True).prefetch_related('images')

    for produto in produtos_da_categoria:
        imagem_selecionada = produto.images.filter(is_main=True).first()
        if not imagem_selecionada:
            imagem_selecionada = produto.images.first()
        produto.imagem_do_card = imagem_selecionada

    nome_categoria_exibicao = categoria_slug.replace('_', ' ').title()

    categorias_para_template = [
        {'nome_url': cat, 'nome_exibicao': cat.replace('_', ' ').title()}
        for cat in categorias_validas
    ]

    context = {
        'categoria_atual': nome_categoria_exibicao,
        'produtos': produtos_da_categoria,
        'categorias_ativas': categorias_para_template,
    }
    return render(request, 'produtos/produtos_por_categoria.html', context)


def produto_detalhe(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, is_active=True)

    imagem_para_exibir = produto.images.filter(is_main=True).first()
    if not imagem_para_exibir:
        imagem_para_exibir = produto.images.first()

    preco_com_desconto = produto.preco or Decimal('0.00')
    preco_original = preco_com_desconto * Decimal('1.2')

    context = {
        'produto': produto,
        'imagem_para_exibir': imagem_para_exibir,
        'preco_com_desconto': preco_com_desconto,
        'preco_original': preco_original,
    }

    return render(request, 'produtos/produto_detalhe.html', context)


def about(request):
    return render(request, 'produtos/about.html')


def contact(request):
    if request.method == "POST":
        # implementar envio de formulário se desejar
        pass
    return render(request, 'produtos/contact.html', {})


def termos_de_servico(request):
    return render(request, 'produtos/termos_de_servico.html', {})


def politica_privacidade(request):
    return render(request, 'produtos/politica_privacidade.html', {})


# --------------------------
# REGISTRO
# --------------------------
def register(request):
    if request.user.is_authenticated:
        messages.info(request, "Você já está logado.")
        return redirect('produtos:home')

    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # marque como cliente se desejar
                user.is_customer = True
                user.save()

                if Cliente is not None:
                    Cliente.objects.create(
                        usuario=user,
                        nome=form.cleaned_data.get('username', ''),
                        email=form.cleaned_data.get('email', ''),
                        telefone=form.cleaned_data.get('telefone', ''),
                        cpf=form.cleaned_data.get('cpf', ''),
                        rua=form.cleaned_data.get('rua', ''),
                        numero=form.cleaned_data.get('numero', ''),
                        cep=form.cleaned_data.get('cep', ''),
                        cidade=form.cleaned_data.get('cidade', ''),
                        estado=form.cleaned_data.get('estado', ''),
                        possui_whatsapp=form.cleaned_data.get('possui_whatsapp', False),
                    )

                login(request, user)
                messages.success(request, 'Cadastro realizado e login efetuado com sucesso!')
                return redirect('produtos:home')

            except IntegrityError:
                messages.error(request, 'Já existe um usuário com este nome de usuário, e-mail, CPF ou CNPJ. Por favor, verifique seus dados.')
            except Exception as e:
                messages.error(request, f"Ocorreu um erro inesperado no registro: {e}")
    else:
        form = CustomRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# --------------------------
# CARRINHO
# --------------------------
def _get_first_image_url(produto):
    """Retorna URL da imagem principal ou primeira, ou string vazia."""
    if not produto:
        return ''
    main_image = produto.images.filter(is_main=True).first()
    if main_image and getattr(main_image, 'image', None):
        return main_image.image.url
    first = produto.images.first()
    if first and getattr(first, 'image', None):
        return first.image.url
    return ''


def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)

    # Pega imagem principal ou primeira
    first_image_url = _get_first_image_url(produto)

    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)

    if not produto.preco or produto.preco <= 0:
        messages.error(request, f'O produto "{produto.name}" está sem preço válido.')
        return redirect('produtos:home')

    # Armazenar preços como string para evitar problemas com float na sessão
    preco_str = str(produto.preco)

    if produto_id_str in carrinho:
        # incrementa quantidade
        try:
            carrinho[produto_id_str]['quantidade'] = int(carrinho[produto_id_str].get('quantidade', 0)) + 1
        except Exception:
            carrinho[produto_id_str]['quantidade'] = 1
        # recalcula subtotal usando Decimal
        qtd = int(carrinho[produto_id_str]['quantidade'])
        subtotal = (Decimal(carrinho[produto_id_str]['preco_unitario']) * qtd) if isinstance(carrinho[produto_id_str]['preco_unitario'], str) or isinstance(carrinho[produto_id_str]['preco_unitario'], Decimal) else Decimal(preco_str) * qtd
        # sempre armazenar como string
        carrinho[produto_id_str]['preco_unitario'] = str(preco_str)
        carrinho[produto_id_str]['subtotal'] = str(subtotal)
    else:
        carrinho[produto_id_str] = {
            'produto_id': produto.id,
            'nome': produto.name,
            'preco_unitario': str(preco_str),
            'quantidade': 1,
            'imagem': first_image_url,
            'description': produto.description or '',
            'subtotal': str(Decimal(preco_str)),
        }

    request.session['carrinho'] = carrinho
    request.session.modified = True
    messages.success(request, f'Produto "{produto.name}" adicionado ao carrinho.')

    return redirect('produtos:ver_carrinho')


@require_POST
def remover_do_carrinho(request, produto_id):
    """
    Se 'acao' == 'menos' e quantidade > 1 => decrementa quantidade.
    Caso contrário remove o item do carrinho.
    """
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)
    acao = request.POST.get('acao', 'remover')

    if produto_id_str in carrinho:
        if acao == 'menos':
            try:
                quantidade_atual = int(carrinho[produto_id_str].get('quantidade', 1))
            except Exception:
                quantidade_atual = 1

            if quantidade_atual > 1:
                quantidade_atual -= 1
                carrinho[produto_id_str]['quantidade'] = quantidade_atual
                try:
                    pu = Decimal(str(carrinho[produto_id_str]['preco_unitario']))
                except Exception:
                    pu = Decimal('0.00')
                carrinho[produto_id_str]['subtotal'] = str(pu * quantidade_atual)
                messages.success(request, "Uma unidade foi removida do carrinho.")
            else:
                # se for 1 e pediu 'menos', remove tudo
                del carrinho[produto_id_str]
                messages.success(request, "Produto removido do carrinho.")
        else:
            # remover tudo
            del carrinho[produto_id_str]
            messages.success(request, "Produto removido do carrinho.")

        request.session['carrinho'] = carrinho
        request.session.modified = True
    else:
        messages.error(request, "Item não encontrado no carrinho.")

    return redirect('produtos:ver_carrinho')


def ver_carrinho(request):
    """
    Monta itens_carrinho com objetos Produto do DB e calcula totais com Decimal.
    Não levanta 404 para itens removidos, apenas os ignora.
    """
    carrinho_atual = request.session.get('carrinho', {})
    itens_carrinho = []
    total_carrinho = Decimal('0.00')
    novo_carrinho_sessao = {}

    for produto_id_str, dados_item in list(carrinho_atual.items()):
        try:
            # valida campos essenciais
            if 'quantidade' not in dados_item or 'preco_unitario' not in dados_item or 'nome' not in dados_item:
                messages.error(request, f"Dados incompletos no carrinho (ID: {produto_id_str}). Item ignorado.")
                continue

            # busca produto no banco, mas não 404: apenas ignora se não existir
            try:
                produto_db = Produto.objects.filter(pk=int(produto_id_str)).first()
            except Exception:
                produto_db = None

            if not produto_db:
                messages.warning(request, f"Produto '{dados_item.get('nome', produto_id_str)}' não encontrado e foi removido.")
                continue

            quantidade = int(dados_item.get('quantidade', 0))
            if quantidade <= 0:
                continue

            # converte preco_unitario vindo da sessão (string) para Decimal
            try:
                preco_unitario_item = Decimal(str(dados_item['preco_unitario']))
            except Exception:
                preco_unitario_item = Decimal('0.00')

            subtotal_item = preco_unitario_item * quantidade
            total_carrinho += subtotal_item

            itens_carrinho.append({
                'produto': produto_db,
                'quantidade': quantidade,
                'preco_unitario': preco_unitario_item,
                'subtotal': subtotal_item,
                'imagem': dados_item.get('imagem', _get_first_image_url(produto_db)),
            })

            # mantemos o item no novo carrinho (serialized) atualizando subtotal/quantidade como strings
            novo_item = {
                'produto_id': dados_item.get('produto_id', produto_id_str),
                'nome': dados_item.get('nome', produto_db.name),
                'preco_unitario': str(preco_unitario_item),
                'quantidade': quantidade,
                'imagem': dados_item.get('imagem', _get_first_image_url(produto_db)),
                'description': dados_item.get('description', produto_db.description or ''),
                'subtotal': str(subtotal_item),
            }
            novo_carrinho_sessao[produto_id_str] = novo_item

        except (ValueError, InvalidOperation) as e:
            messages.warning(request, f"Erro ao processar item {produto_id_str}: {e}")
            continue
        except Exception as e:
            messages.error(request, f"Erro inesperado no item {produto_id_str}: {e}")
            continue

    # atualiza sessão com itens válidos
    request.session['carrinho'] = novo_carrinho_sessao
    request.session.modified = True

    # Frete
    valor_frete = request.session.get('valor_frete')
    try:
        frete_decimal = Decimal(str(valor_frete)) if valor_frete is not None else Decimal("0.00")
    except Exception:
        messages.warning(request, "Erro ao carregar valor do frete. Será recalculado.")
        frete_decimal = Decimal("0.00")

    total_com_frete = total_carrinho + frete_decimal

    total_itens = sum(item['quantidade'] for item in itens_carrinho)

    context = {
        'itens_carrinho': itens_carrinho,
        'total_carrinho': total_carrinho,
        'frete': frete_decimal,
        'total_com_frete': total_com_frete,
        'total_itens': total_itens,
    }

    return render(request, 'produtos/ver_carrinho.html', context)


# --------------------------
# BUSCA
# --------------------------
def search(request):
    query = request.GET.get('q')
    produtos_encontrados = []

    if query:
        produtos_encontrados = Produto.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        ).distinct().prefetch_related('images')

        # opcional: log para debug
        for p in produtos_encontrados:
            # print pode ajudar ao debugar nos logs do container
            print(f"   - ID: {p.id}, Nome: {p.name}, Ativo: {p.is_active}, Descrição: {p.description}")

    return render(request, 'produtos/search_results.html', {'query': query, 'produtos': produtos_encontrados})


# --------------------------
# CÁLCULO DE FRETE
# --------------------------
def calcular_frete(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    imagem_para_exibir = produto.images.filter(is_main=True).first()
    if not imagem_para_exibir:
        imagem_para_exibir = produto.images.first()

    preco_com_desconto = produto.preco or Decimal('0.00')
    preco_original = preco_com_desconto * Decimal('1.2')

    if request.method == 'POST':
        cep = request.POST.get('cep', '').replace('-', '').strip()

        if len(cep) < 3:
            return render(request, 'produtos/produto_detalhe.html', {
                'produto': produto,
                'imagem_para_exibir': imagem_para_exibir,
                'preco_original': preco_original,
                'preco_com_desconto': preco_com_desconto,
                'frete_indisponivel': True,
            })

        prefixo = cep[:3]
        regiao = RegiaoFrete.objects.filter(prefixo_cep=prefixo).first()

        if regiao:
            request.session['valor_frete'] = float(regiao.valor_frete)
            request.session.modified = True

            return render(request, 'produtos/produto_detalhe.html', {
                'produto': produto,
                'imagem_para_exibir': imagem_para_exibir,
                'preco_original': preco_original,
                'preco_com_desconto': preco_com_desconto,
                'frete_disponivel': True,
                'valor_frete': f"{regiao.valor_frete:.2f}",
                'prazo': regiao.prazo_entrega,
            })
        else:
            return render(request, 'produtos/produto_detalhe.html', {
                'produto': produto,
                'imagem_para_exibir': imagem_para_exibir,
                'preco_original': preco_original,
                'preco_com_desconto': preco_com_desconto,
                'frete_indisponivel': True,
            })

    return render(request, 'produtos/produto_detalhe.html', {
        'produto': produto,
        'imagem_para_exibir': imagem_para_exibir,
        'preco_com_desconto': preco_com_desconto,
    })


@require_POST
def calcular_frete_carrinho(request):
    cep = request.POST.get('cep', '').replace('-', '').strip()
    if len(cep) < 3:
        messages.error(request, "CEP inválido para cálculo do frete.")
        return redirect('produtos:ver_carrinho')

    prefixo = cep[:3]
    regiao = RegiaoFrete.objects.filter(prefixo_cep=prefixo).first()

    if regiao:
        request.session['valor_frete'] = float(regiao.valor_frete)
        request.session.modified = True
        messages.success(request, f"Frete para o CEP {cep} calculado com sucesso.")
    else:
        messages.error(request, f"Não encontramos uma região com base no CEP informado ({cep}).")

    return redirect('produtos:ver_carrinho')


# --------------------------
# PEDIDOS
# --------------------------
@login_required
def lista_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'produtos/lista_pedidos.html', {'pedidos': pedidos})


@login_required
def detalhe_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'produtos/detalhe_pedido.html', {'pedido': pedido})


def portfolio_completo(request):
    """
    Renderiza a página com a galeria completa de todos os projetos executados.
    """
    # Esta linha agora é válida porque ProjetoExecutado foi importado acima
    todos_projetos = ProjetoExecutado.objects.filter(is_active=True).order_by('-potencia_kwp', 'localidade')
    
    context = {
        'todos_projetos': todos_projetos,
    }
    # O template continua sendo renderizado da pasta 'produtos'
    return render(request, 'produtos/portfolio_completo.html', context)


from math import pow
# ... (suas outras importações no topo do arquivo)

# =========================================================
# VIEWS DE SIMULAÇÃO (ECONOMIA E FINANCIAMENTO)
# =========================================================

def simulador_solar(request):
    """
    Renderiza a página de simulação de economia e calcula os resultados (MOCK).
    Esta view precisa estar aqui para o link 'simulador_solar' funcionar.
    """
    resultado_simulacao = None
    
    if request.method == 'POST':
        # 1. Coletar Dados do Formulário
        consumo_kwh = request.POST.get('consumo_kwh')
        # Outros campos: cep, nome, email, se existirem no seu template
        
        # 2. Simulação e Cálculo (MOCK/SIMULADO)
        try:
            consumo_kwh = int(consumo_kwh)
            
            # Lógica simples de estimativa
            potencia_kwp_estimada = round(consumo_kwh * 1.5 / 1000, 2)
            economia_mensal_estimada = round(consumo_kwh * 0.85 * 0.70, 2) 

            resultado_simulacao = {
                'consumo_kwh': consumo_kwh,
                'potencia_kwp': potencia_kwp_estimada,
                'economia_mensal': economia_mensal_estimada,
                # ... outros dados
            }
            
            # Se fosse real, aqui enviaria o lead para o CRM
            
        except ValueError:
            return render(request, 'produtos/simulador_solar.html', {'error': 'Por favor, insira um valor válido para o consumo.'})
        
    context = {
        'resultado': resultado_simulacao,
    }
    return render(request, 'produtos/simulador_solar.html', context)


def simular_financiamento(request):
    """
    Renderiza a página de simulação de financiamento e calcula as parcelas (MOCK).
    """
    simulacoes = []
    valor_total = None
    erro_mensagem = None

    if request.method == 'POST':
        try:
            valor_input = request.POST.get('valor_total').replace(',', '.')
            valor_total = float(valor_input)
            
            TAXA_MENSAL_MOCK = 0.0195 # 1.95% a.m. (Mock)
            PRAZOS = [24, 36, 48, 60, 72]
            
            for n_parcelas in PRAZOS:
                i = TAXA_MENSAL_MOCK
                fator = (i * pow(1 + i, n_parcelas)) / (pow(1 + i, n_parcelas) - 1)
                valor_parcela = valor_total * fator
                
                simulacoes.append({
                    'parcelas': n_parcelas,
                    'valor_parcela': round(valor_parcela, 2),
                    'total_pago': round(valor_parcela * n_parcelas, 2),
                    'taxa_mensal': round(i * 100, 2)
                })

        except ValueError:
            erro_mensagem = "Por favor, insira um valor válido."
        except Exception as e:
            erro_mensagem = "Ocorreu um erro no cálculo. Tente novamente."

    context = {
        'valor_total': valor_total,
        'simulacoes': simulacoes,
        'erro_mensagem': erro_mensagem,
    }
    return render(request, 'produtos/simulador_financiamento.html', context)



def rastreio_proposta(request):
    """
    Renderiza a página de rastreamento e busca a proposta pelo número e CPF/CNPJ.
    """
    proposta = None
    erro_mensagem = None
    
    if request.method == 'POST':
        numero_proposta = request.POST.get('numero_proposta').strip()
        cpf_cnpj = request.POST.get('cpf_cnpj').strip()

        if not numero_proposta or not cpf_cnpj:
            erro_mensagem = "Por favor, preencha o número da proposta e o CPF/CNPJ."
        else:
            try:
                proposta = Proposta.objects.get(
                    numero__iexact=numero_proposta, 
                    cpf_cnpj__iexact=cpf_cnpj
                )
            except Proposta.DoesNotExist:
                erro_mensagem = "Proposta não encontrada. Verifique os dados e tente novamente."
            except Exception as e:
                erro_mensagem = f"Ocorreu um erro: {e}"

    context = {
        'proposta': proposta,
        'erro_mensagem': erro_mensagem
    }
    # O template de rastreio também precisa existir na sua pasta 'produtos/templates/produtos/'
    return render(request, 'produtos/rastreio_proposta.html', context)

