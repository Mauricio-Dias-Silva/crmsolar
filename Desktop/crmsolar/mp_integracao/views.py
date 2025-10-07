import json
import logging
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from mercadopago.sdk import SDK

from produtos.models import Pedido, Produto
from solar.models import Cliente
from .models import TransacaoMercadoPago

logger = logging.getLogger(__name__)

# =========================
# SDK Mercado Pago
# =========================
mp_sdk = SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

# =========================
# Utilitários
# =========================
def _dec_or_none(value):
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None

def _abs_url(request, route_name):
    """
    Gera URL absoluta para callback do Mercado Pago.
    Se estiver em ngrok, respeita o domínio atual.
    Caso contrário, usa request.build_absolute_uri.
    """
    host = request.get_host()
    path = reverse(route_name)
    if "ngrok-free.app" in host:
        return f"https://{host}{path}"
    return request.build_absolute_uri(path)

# =========================
# Atualizar status do pedido
# =========================
def atualizar_status_pagamento(pedido, status_pagamento_mp):
    if status_pagamento_mp == 'approved':
        pedido.status = 'pago'
        pedido.data_pagamento = timezone.now()
        novo_status = 'pago'
    elif status_pagamento_mp == 'pending':
        pedido.status = 'pendente'
        novo_status = 'pendente'
    elif status_pagamento_mp == 'rejected':
        pedido.status = 'cancelado'
        novo_status = 'cancelado'
    else:
        novo_status = status_pagamento_mp

    pedido.save()
    TransacaoMercadoPago.objects.filter(pedido=pedido).update(
        status=novo_status,
        data_atualizacao=timezone.now()
    )

# =========================
# Fluxo de Pagamento
# =========================
@login_required
def iniciar_pagamento_selecionado_flow(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, "O carrinho está vazio.")
        return redirect('produtos:ver_carrinho')

    itens_mp = []
    total_calculado = Decimal('0.00')

    for produto_id_str, item in carrinho.items():
        nome = item.get('nome') or item.get('title') or "Produto"
        preco = _dec_or_none(item.get('preco_unitario') or item.get('unit_price'))
        qtd = item.get('quantidade') or item.get('quantity') or 1

        if preco is None or preco <= 0:
            messages.error(request, f"O item '{nome}' tem preço inválido.")
            return redirect('produtos:ver_carrinho')

        itens_mp.append({
            "title": nome,
            "quantity": int(qtd),
            "unit_price": float(preco),
        })
        total_calculado += preco * int(qtd)

    preference_data = {
        "items": itens_mp,
        "back_urls": {
            "success": _abs_url(request, "mp_integracao:pagamento_sucesso"),
            "failure": _abs_url(request, "mp_integracao:pagamento_falha"),
            "pending": _abs_url(request, "mp_integracao:pagamento_pendente"),
        },
        "auto_return": "approved",
        "external_reference": str(request.user.id),
    }
    logger.info("Dados de preferência enviados ao Mercado Pago: %s", preference_data)

    try:
        result = mp_sdk.preference().create(preference_data)

        if "response" in result and "id" in result["response"]:
            preference_id = result["response"]["id"]
        else:
            messages.error(request, f"Não foi possível criar a preferência no Mercado Pago. Retorno: {result}")
            return redirect('produtos:ver_carrinho')

        request.session['mp_preference_id'] = preference_id
        request.session.modified = True

        return redirect(f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id={preference_id}")

    except Exception as e:
        logger.error("Erro ao criar pagamento no Mercado Pago: %s", e, exc_info=True)
        messages.error(request, f"Erro ao criar pagamento: {e}")
        return redirect('produtos:ver_carrinho')

# =========================
# Webhook Mercado Pago
# =========================
@csrf_exempt
def webhook_mercado_pago(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body or "{}")
        topic = data.get('topic') or data.get('type')
        payment_id = data.get('data', {}).get('id')

        if topic != 'payment' or not payment_id:
            logger.warning("Webhook sem ID de pagamento válido.")
            return HttpResponse(status=400)

        sdk = SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment_id)

        if payment_info.get('status') == 200:
            status_pagamento_mp = payment_info['response'].get('status')
            pedido_id = payment_info['response'].get('external_reference')

            if pedido_id:
                try:
                    pedido = Pedido.objects.get(pk=pedido_id)
                    atualizar_status_pagamento(pedido, status_pagamento_mp)
                    logger.info("Pagamento %s do Pedido %s -> %s", payment_id, pedido.id, status_pagamento_mp)
                except Pedido.DoesNotExist:
                    logger.warning("Pedido %s não encontrado no webhook (payment_id=%s).", pedido_id, payment_id)

        return HttpResponse(status=200)
    except Exception as e:
        logger.error("Erro no webhook do Mercado Pago: %s", e, exc_info=True)
        return HttpResponse(status=500)

# =========================
# Callbacks de retorno
# =========================
def pagamento_sucesso(request):
    messages.success(request, "Seu pagamento foi aprovado! Obrigado pela compra.")
    return render(request, 'mp_integracao/pagamento_sucesso.html')

def pagamento_falha(request):
    messages.error(request, "Seu pagamento falhou. Tente novamente.")
    return render(request, 'mp_integracao/pagamento_falha.html')

def pagamento_pendente(request):
    messages.info(request, "Seu pagamento está pendente de aprovação.")
    return render(request, 'mp_integracao/pagamento_pendente.html')

# =========================
# Seleção de itens → inicia fluxo
# =========================
@login_required
@require_POST
def processar_pagamento_selecionado(request):
    itens_selecionados_ids = request.POST.getlist('itens_selecionados')
    if not itens_selecionados_ids:
        messages.warning(request, "Nenhum item foi selecionado para pagamento.")
        return redirect('produtos:ver_carrinho')

    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('produtos:ver_carrinho')

    itens_para_pagamento = {}
    for item_id in itens_selecionados_ids:
        if item_id in carrinho:
            itens_para_pagamento[item_id] = carrinho[item_id]
        else:
            messages.warning(request, f"O item {item_id} não está mais no carrinho.")

    if not itens_para_pagamento:
        messages.error(request, "Nenhum dos itens selecionados está disponível no carrinho.")
        return redirect('produtos:ver_carrinho')

    request.session['itens_pagamento_atual'] = itens_para_pagamento
    request.session.modified = True
    return iniciar_pagamento_selecionado_flow(request)
