# pagamentos/urls.py

from django.urls import path
from . import views

app_name = 'pagamentos'

urlpatterns = [
    # URLs genéricas para iniciar e retornar pagamentos
    path('iniciar/<str:model_name>/<int:entity_id>/', views.iniciar_pagamento_mp, name='iniciar_pagamento_mp'),
    path('notificacao/', views.notificacao_pagamento_mp, name='notificacao_pagamento_mp'),
    path('retorno/sucesso/<str:model_name>/<int:entity_id>/', views.retorno_pagamento_sucesso, name='retorno_pagamento_sucesso'),
    path('retorno/pendente/<str:model_name>/<int:entity_id>/', views.retorno_pagamento_pendente, name='retorno_pagamento_pendente'),
    path('retorno/falha/<str:model_name>/<int:entity_id>/', views.retorno_pagamento_falha, name='retorno_pagamento_falha'),
]