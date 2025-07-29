# pagamentos/views.py

import mercadopago
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt 
from django.db import transaction
import json
import logging
from django.urls import reverse 

# Importe todos os modelos que podem ser origem de um pagamento
from compras.models import Compra, Cupom 
from ofertas.models import Oferta 
from pedidos_coletivos.models import PedidoColetivo 

# pagamentos/views.py

# ... (imports existentes) ...

logger = logging.getLogger(__name__)
sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

def iniciar_pagamento_mp(request, model_name, entity_id):
    model_map = {
        'compra': Compra,
        'pedidocoletivo': PedidoColetivo,
    }
    
    EntityModel = model_map.get(model_name.lower())
    if not EntityModel:
        messages.error(request, 'Tipo de entidade de pagamento inválido.')
        return redirect('ofertas:lista_oferta') 

    entidade_pagamento = get_object_or_404(EntityModel, id=entity_id, usuario=request.user)

    if entidade_pagamento.id_preferencia_mp:
        if settings.DEBUG:
            return redirect(f"https://www.mercadopago.com.br/sandbox/payments/checkout/decision?pref_id={entidade_pagamento.id_preferencia_mp}")
        else:
            return redirect(f"https://www.mercadopago.com.br/payments/checkout/decision?pref_id={entidade_pagamento.id_preferencia_mp}")

    # <--- NOVO: Pega o valor final da sessão, se estiver lá
    valor_a_cobrar = request.session.pop('valor_a_cobrar_mp', None) 
    if valor_a_cobrar is None: # Se não veio da sessão, usa o valor total da entidade
        valor_a_cobrar = float(entidade_pagamento.valor_total)

    # Cria o item com o valor a ser cobrado
    item = {
        "title": entidade_pagamento.oferta.titulo,
        "quantity": 1, # Quantidade sempre 1 para representar o total do pedido
        "unit_price": float(valor_a_cobrar), # <--- Usa o valor_a_cobrar aqui
        "currency_id": "BRL", 
    }
    
    base_url = request.build_absolute_uri('/')[:-1] 
    
    success_url = request.build_absolute_uri(reverse('pagamentos:retorno_pagamento_sucesso', args=[model_name, entidade_pagamento.id]))
    pending_url = request.build_absolute_uri(reverse('pagamentos:retorno_pagamento_pendente', args=[model_name, entidade_pagamento.id]))
    failure_url = request.build_absolute_uri(reverse('pagamentos:retorno_pagamento_falha', args=[model_name, entidade_pagamento.id]))
    
    notification_url = request.build_absolute_uri(reverse('pagamentos:notificacao_pagamento_mp'))
    
    preference_data = {
        "items": [item],
        "payer": {
            "name": request.user.first_name if request.user.first_name else request.user.username,
            "surname": request.user.last_name if request.user.last_name else "",
            "email": request.user.email,
        },
        "external_reference": f"{model_name.lower()}_{entidade_pagamento.id}", 
        "notification_url": notification_url, 
        "auto_return": "all", 
        "back_urls": {
            "success": success_url,
            "pending": pending_url,
            "failure": failure_url,
        },
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        entidade_pagamento.id_preferencia_mp = preference["id"]
        entidade_pagamento.save()

        if settings.DEBUG: 
            return redirect(preference["sandbox_init_point"])
        else:
            return redirect(preference["init_point"])

    except Exception as e:
        logger.error(f"Erro ao criar preferência de pagamento para {model_name} {entidade_pagamento.id}: {e}", exc_info=True)
        messages.error(request, f"Não foi possível iniciar o pagamento. Erro: {e}")
        return redirect('ofertas:detalhe_oferta', slug_oferta=entidade_pagamento.oferta.slug)

# ... (notificacao_pagamento_mp e funções de retorno - permanecem as mesmas) ...


@csrf_exempt 
def notificacao_pagamento_mp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Notificação Mercado Pago recebida: {data}")

            topic = request.GET.get('topic') or data.get('type') 
            resource_id = request.GET.get('id') or data.get('data', {}).get('id')

            if topic == 'payment' and resource_id:
                payment_info = sdk.payment().get(resource_id)
                payment_status = payment_info["response"]["status"]
                external_reference = payment_info["response"].get("external_reference") 
                
                logger.info(f"Processando notificação - Payment ID: {resource_id}, Status: {payment_status}, External Ref: {external_reference}")

                if external_reference and '_' in external_reference:
                    model_name_str, entity_id_str = external_reference.split('_', 1)
                    entity_id = int(entity_id_str)

                    try:
                        with transaction.atomic():
                            entidade_pagamento = None
                            if model_name_str == 'compra':
                                entidade_pagamento = Compra.objects.get(id=entity_id)
                            elif model_name_str == 'pedidocoletivo':
                                entidade_pagamento = PedidoColetivo.objects.get(id=entity_id)
                            
                            if entidade_pagamento:
                                oferta = entidade_pagamento.oferta 

                                if payment_status == 'approved':
                                    if isinstance(entidade_pagamento, Compra): 
                                        if entidade_pagamento.status_pagamento != 'aprovada':
                                            entidade_pagamento.status_pagamento = 'aprovada'
                                            entidade_pagamento.id_transacao_mp = resource_id
                                            entidade_pagamento.metodo_pagamento = payment_info["response"]["payment_type_id"]
                                            entidade_pagamento.save()

                                            if not hasattr(entidade_pagamento, 'cupom'): 
                                                Cupom.objects.create(
                                                    compra=entidade_pagamento,
                                                    oferta=oferta,
                                                    usuario=entidade_pagamento.usuario,
                                                    valido_ate=oferta.data_termino, 
                                                    status='disponivel'
                                                )
                                                oferta.quantidade_vendida += entidade_pagamento.quantidade
                                                oferta.save()
                                            logger.info(f"Compra {entidade_pagamento.id} por unidade: APROVADA. Cupom gerado/verificado.")

                                    elif isinstance(entidade_pagamento, PedidoColetivo): 
                                        if entidade_pagamento.status_pagamento != 'aprovado_mp':
                                            entidade_pagamento.status_pagamento = 'aprovado_mp' 
                                            entidade_pagamento.id_transacao_mp = resource_id
                                            entidade_pagamento.metodo_pagamento = payment_info["response"]["payment_type_id"]
                                            entidade_pagamento.save()
                                            
                                            oferta.quantidade_vendida += entidade_pagamento.quantidade
                                            oferta.save() 
                                            logger.info(f"Pedido Coletivo {entidade_pagamento.id}: APROVADO NO MP (aguardando lote). Qtd oferta atualizada.")

                                elif payment_status == 'pending':
                                    entidade_pagamento.status_pagamento = 'pendente' 
                                    entidade_pagamento.id_transacao_mp = resource_id
                                    entidade_pagamento.metodo_pagamento = payment_info["response"]["payment_type_id"]
                                    entidade_pagamento.save()
                                    logger.info(f"Entidade {model_name_str} {entidade_pagamento.id} atualizada para PENDENTE.")

                                elif payment_status in ['rejected', 'cancelled']:
                                    entidade_pagamento.status_pagamento = 'recusado'
                                    entidade_pagamento.id_transacao_mp = resource_id
                                    entidade_pagamento.metodo_pagamento = payment_info["response"]["payment_type_id"]
                                    entidade_pagamento.save()
                                    logger.warning(f"Entidade {model_name_str} {entidade_pagamento.id} atualizada para RECUSADO/CANCELADO.")

                                elif payment_status in ['refunded', 'charged_back']:
                                    entidade_pagamento.status_pagamento = 'reembolsada' 
                                    entidade_pagamento.id_transacao_mp = resource_id
                                    entidade_pagamento.metodo_pagamento = payment_info["response"]["payment_type_id"]
                                    entidade_pagamento.save()
                                    logger.info(f"Entidade {model_name_str} {entidade_pagamento.id} atualizada para REEMBOLSADA.")
                            else:
                                logger.error(f"Entidade {model_name_str} não mapeada ou não encontrada para ID {entity_id}.")

                    except (Compra.DoesNotExist, PedidoColetivo.DoesNotExist):
                        logger.error(f"Entidade com external_reference {external_reference} não encontrada no banco de dados.")
                    except Exception as e:
                        logger.error(f"Erro ao processar atualização da entidade {external_reference} na notificação {resource_id}: {e}", exc_info=True)
                else:
                    logger.warning(f"external_reference '{external_reference}' inválido ou não contém o padrão esperado.")
            else:
                logger.info(f"Notificação de tipo '{topic}' com ID '{resource_id}' ignorada ou sem dados relevantes.")

            return HttpResponse(status=200) 

        except json.JSONDecodeError:
            logger.error("Erro ao decodificar JSON da notificação do Mercado Pago.")
            return HttpResponse(status=400)
        except Exception as e:
            logger.error(f"Erro inesperado ao processar notificação do Mercado Pago: {e}", exc_info=True)
            return HttpResponse(status=500)

    return HttpResponse(status=405)


# Ajuste as funções de retorno para aceitar model_name e entity_id
def retorno_pagamento_sucesso(request, model_name, entity_id):
    model_map = {'compra': Compra, 'pedidocoletivo': PedidoColetivo}
    EntityModel = model_map.get(model_name.lower())
    if not EntityModel: messages.error(request, 'Tipo de entidade inválido.'); return redirect('ofertas:lista_ofertas')
    entidade = get_object_or_404(EntityModel, id=entity_id, usuario=request.user)
    messages.success(request, f'Seu pagamento para "{entidade.oferta.titulo}" foi processado! Verifique o status em sua área.')
    # Redireciona para Meus Cupons se for Compra, ou para Meus Pedidos Coletivos se for PedidoColetivo
    if isinstance(entidade, Compra): return redirect('compras:meus_cupons')
    if isinstance(entidade, PedidoColetivo): return redirect('pedidos_coletivos:meus_pedidos') 
    return redirect('ofertas:lista_ofertas')

def retorno_pagamento_pendente(request, model_name, entity_id):
    model_map = {'compra': Compra, 'pedidocoletivo': PedidoColetivo}
    EntityModel = model_map.get(model_name.lower())
    if not EntityModel: messages.error(request, 'Tipo de entidade inválido.'); return redirect('ofertas:lista_ofertas')
    entidade = get_object_or_404(EntityModel, id=entity_id, usuario=request.user)
    messages.info(request, f'Seu pagamento para "{entidade.oferta.titulo}" está pendente. Verifique o status em breve.')
    if isinstance(entidade, Compra): return redirect('compras:meus_cupons')
    if isinstance(entidade, PedidoColetivo): return redirect('pedidos_coletivos:meus_pedidos')
    return redirect('ofertas:lista_ofertas')

def retorno_pagamento_falha(request, model_name, entity_id):
    model_map = {'compra': Compra, 'pedidocoletivo': PedidoColetivo}
    EntityModel = model_map.get(model_name.lower())
    if not EntityModel: messages.error(request, 'Tipo de entidade inválido.'); return redirect('ofertas:lista_ofertas')
    entidade = get_object_or_404(EntityModel, id=entity_id, usuario=request.user)
    messages.error(request, f'Seu pagamento para "{entidade.oferta.titulo}" falhou. Por favor, tente novamente.')
    return redirect('ofertas:detalhe_oferta', slug_oferta=entidade.oferta.slug)