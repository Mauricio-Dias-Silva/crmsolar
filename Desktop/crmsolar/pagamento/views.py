from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import stripe
from produtos.models import Pedido, Item
from solar.models import Cliente
from django.contrib.auth.decorators import login_required
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def criar_checkout_session(request):
    if not request.session.get('carrinho'):
        messages.error(request, "Seu carrinho está vazio. Adicione produtos para continuar.")
        return redirect('produtos:home')

    carrinho = request.session.get('carrinho', {})
    line_items = []
    
    try:
        try:
            cliente = request.user.perfil_cliente
            email_cliente = cliente.email
        except Cliente.DoesNotExist:
            messages.error(request, "Seu perfil de cliente não foi encontrado. Por favor, entre em contato com o suporte.")
            return redirect('produtos:ver_carrinho')

        total_carrinho = sum(Decimal(str(item['subtotal'])) for item in carrinho.values())
        valor_frete = Decimal(str(request.session.get('valor_frete', '0.00')))
        
        pedido = Pedido.objects.create(
            usuario=request.user,
            email_cliente=email_cliente,
            total=total_carrinho + valor_frete,
            status='pendente',
            metodo_pagamento='stripe'
        )

        for item_data in carrinho.values():
            Item.objects.create(
                pedido=pedido,
                nome=item_data['nome'],
                preco_unitario=Decimal(str(item_data['preco_unitario'])),
                quantidade=item_data['quantidade'],
                subtotal=Decimal(str(item_data['subtotal']))
            )
            line_items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': item_data['nome'],
                    },
                    'unit_amount': int(Decimal(str(item_data['preco_unitario'])) * 100),
                },
                'quantity': item_data['quantidade'],
            })
            
        if valor_frete > 0:
             line_items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': 'Frete',
                    },
                    'unit_amount': int(valor_frete * 100),
                },
                'quantity': 1,
            })

        success_url = request.build_absolute_uri(reverse('pagamento:compra_sucesso')) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = request.build_absolute_uri(reverse('pagamento:pagamento_cancelado'))

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'pedido_id': str(pedido.id)}
        )
        
        request.session['carrinho'] = {}
        request.session.modified = True
        
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        messages.error(request, f"Ocorreu um erro inesperado ao iniciar o checkout: {e}")
        return redirect('produtos:ver_carrinho')

def compra_sucesso(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            pedido_id = checkout_session.metadata.get('pedido_id')
            pedido = Pedido.objects.get(id=pedido_id)
            
            if checkout_session.payment_status == 'paid':
                pedido.status = 'pago'
                pedido.stripe_id = session_id
                pedido.save()
                messages.success(request, "Seu pagamento foi aprovado! Obrigado pela compra.")
            else:
                messages.warning(request, "O pagamento ainda está pendente ou não foi concluído.")
            
            # NOVO: Passa o pedido para o contexto do template
            context = {
                'pedido': pedido,
                'checkout_session': checkout_session,
            }
            return render(request, 'pagamento/compra_sucesso.html', context)

        except Pedido.DoesNotExist:
            messages.error(request, "O pedido não foi encontrado. Por favor, entre em contato com o suporte.")
        except stripe.error.StripeError as e:
            messages.error(request, f"Erro ao processar o pagamento: {e}")

    messages.error(request, "Não foi possível confirmar o status do pagamento. Por favor, entre em contato com o suporte.")
    return redirect('produtos:home')

def pagamento_cancelado(request):
    messages.info(request, "O pagamento foi cancelado. Você pode tentar novamente.")
    return render(request, 'pagamento/pagamento_cancelado.html')
