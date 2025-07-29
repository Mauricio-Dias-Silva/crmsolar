# compras/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.db import transaction 
from django.utils import timezone 
import uuid 

from ofertas.models import Oferta 
from .models import Compra, Cupom 
from pedidos_coletivos.models import CreditoUsuario # <--- NOVO: Importar CreditoUsuario

from django.urls import reverse 

@login_required 
def comprar_oferta(request, slug_oferta):
    oferta = get_object_or_404(
        Oferta, 
        slug=slug_oferta,
        publicada=True,
        status__in=['ativa', 'sucesso'], 
        data_termino__gte=timezone.now() 
    )

    if not oferta.esta_disponivel_para_compra:
        messages.error(request, 'Esta oferta não está mais disponível para compra.')
        return redirect('ofertas:detalhe_oferta', slug_oferta=oferta.slug)

    # Redireciona para o fluxo de pedido coletivo se for oferta de lote
    if oferta.tipo_oferta == 'lote':
        messages.info(request, 'Esta é uma oferta de compra coletiva. Redirecionando para o processo de pedido coletivo.')
        return redirect('pedidos_coletivos:fazer_pedido_coletivo', slug_oferta=oferta.slug)

    # Lógica para ofertas de 'unidade'
    # Obtém o saldo de crédito do usuário
    credito_usuario, created = CreditoUsuario.objects.get_or_create(usuario=request.user)
    saldo_disponivel = credito_usuario.saldo

    valor_total_compra = oferta.preco_desconto # Valor total para esta compra (1 unidade)
    valor_a_pagar_mp = valor_total_compra
    usar_credito_total = False # Flag para indicar se o crédito cobriu tudo

    if request.method == 'POST':
        usar_credito = request.POST.get('usar_credito') == 'on' # Verifica o checkbox

        if usar_credito and saldo_disponivel > 0:
            if saldo_disponivel >= valor_total_compra:
                # Crédito cobre o valor total
                valor_a_pagar_mp = 0.00
                usar_credito_total = True
            else:
                # Crédito cobre parcialmente
                valor_a_pagar_mp = valor_total_compra - saldo_disponivel
                # O restante será pago pelo Mercado Pago.
            
        try:
            with transaction.atomic():
                compra = Compra.objects.create(
                    usuario=request.user,
                    oferta=oferta,
                    quantidade=1, 
                    valor_total=valor_total_compra, # Valor total da compra original
                    status_pagamento='pendente', # Status inicial padrão
                )

                if usar_credito_total:
                    # Se o crédito cobriu tudo, a compra é aprovada imediatamente
                    credito_usuario.usar_credito(valor_total_compra, 
                                                 f"Pagamento da oferta '{oferta.titulo}' (Compra #{compra.id})")
                    compra.status_pagamento = 'aprovada'
                    compra.metodo_pagamento = 'Credito do Site'
                    compra.save()

                    # Gera o cupom imediatamente
                    Cupom.objects.create(
                        compra=compra,
                        oferta=oferta,
                        usuario=request.user,
                        valido_ate=oferta.data_termino, 
                        status='disponivel'
                    )
                    oferta.quantidade_vendida += compra.quantidade
                    oferta.save()
                    messages.success(request, f'Sua compra para "{oferta.titulo}" foi aprovada usando seu crédito! Cupom gerado.')
                    return redirect('compras:meus_cupons')
                else:
                    # Redireciona para o Mercado Pago com o valor restante a pagar
                    messages.info(request, 'Redirecionando para o Mercado Pago para finalizar a compra...')
                    # Passa o valor_a_pagar_mp para a view de pagamento
                    # (A view de MP precisa ser adaptada para aceitar um 'amount' customizado,
                    # ou o item do MP precisa ser calculado com base nisso)
                    
                    # Para simplificar, vou fazer com que o iniciar_pagamento_mp sempre pegue o valor_total da compra,
                    # e o desconto do crédito será tratado APÓS o pagamento do MP, ou antes de gerar a preferência.
                    # Mudei a preferência do MP para aceitar valor total do pedido, e quantity=1
                    
                    # A melhor forma é passar o valor final para o Mercado Pago, 
                    # então precisamos ajustar iniciar_pagamento_mp para aceitar um 'override_value'
                    # ou criar a preferência com o 'valor_a_pagar_mp'

                    # **Opção mais simples (menos refatoração no MP):**
                    # Criar a Preferência MP com o valor total da compra e lidar com o crédito depois.
                    # Mas se o usuário usou crédito parcial, o valor no MP DEVE ser o restante.
                    # Vamos adaptar iniciar_pagamento_mp para aceitar um valor final se for passado.
                    
                    # Vamos passar o valor_a_pagar_mp como um parâmetro extra na URL ou session para iniciar_pagamento_mp
                    # ou fazer o cálculo dentro de iniciar_pagamento_mp.
                    
                    # **Decisão de Design:** É mais limpo que a view de pagamento (iniciar_pagamento_mp) receba o VALOR EXATO
                    # que deve ser cobrado. Então, vamos adicionar esse valor ao `request.session` ou passá-lo para a URL.
                    
                    request.session['valor_a_cobrar_mp'] = float(valor_a_pagar_mp)
                    return redirect(reverse('pagamentos:iniciar_pagamento_mp', args=['compra', compra.id]))

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao preparar sua compra: {e}. Por favor, tente novamente.')
            return redirect('ofertas:detalhe_oferta', slug_oferta=oferta.slug)
    
    contexto = {
        'oferta': oferta,
        'saldo_disponivel': saldo_disponivel,
        'valor_total_compra': valor_total_compra,
        'titulo_pagina': f'Confirmar Compra: {oferta.titulo}'
    }
    return render(request, 'compras/confirmar_compra.html', contexto)



@login_required
def meus_cupons(request):
    """
    Visualização para listar todos os cupons comprados pelo usuário logado.
    """
    # Busca todos os cupons do usuário atual, ordenados pelo mais recente
    cupons = Cupom.objects.filter(usuario=request.user).order_by('-data_geracao')

    contexto = {
        'cupons': cupons,
        'titulo_pagina': 'Meus Cupons'
    }
    return render(request, 'compras/meus_cupons.html', contexto)