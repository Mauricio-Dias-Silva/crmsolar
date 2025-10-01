from django.urls import path
from . import views

# CORREÇÃO AQUI
app_name = "mp_integracao"

urlpatterns = [
    # Início do pagamento
    path("iniciar/", views.iniciar_pagamento_selecionado_flow, name="iniciar_pagamento_selecionado_flow"),
    
    # Callbacks de redirecionamento (sucesso, falha, pendente)
    path("sucesso/", views.pagamento_sucesso, name="pagamento_sucesso"),
    path("falha/", views.pagamento_falha, name="pagamento_falha"),
    path("pendente/", views.pagamento_pendente, name="pagamento_pendente"),

    # Webhook do Mercado Pago
    path("webhook/", views.webhook_mercado_pago, name="webhook_mercado_pago"),

    # Seleção do método de pagamento (Mercado Pago ou Stripe)
    path("processar/", views.processar_pagamento_selecionado, name="processar_pagamento_selecionado"),
    path('pagamento-selecionado/', views.processar_pagamento_selecionado, name='processar_pagamento_selecionado'),
]