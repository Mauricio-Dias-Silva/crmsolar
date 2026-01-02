# SysGov_Project/core/context_processors.py
import datetime
from .models import Notificacao

def global_context(request):
    return {
        'logo_url': 'img/logo_barueri.jpg', # Caminho do seu logo
        'ano_atual': datetime.date.today().year, # Opcional: para o footer de direitos autorais
        # Adicione aqui outras variáveis que você queira que estejam em todos os templates
    }


# core/context_processors.py
from django.core.cache import cache
from .models import Notificacao

def notificacoes_nao_lidas(request):
    if request.user.is_authenticated:
        # Cria uma chave de cache única para este usuário
        cache_key = f'notificacoes_nao_lidas_{request.user.id}'

        # Tenta pegar os dados do cache primeiro
        notificacoes = cache.get(cache_key)

        # Se não estiver no cache (miss), busca no banco
        # Se não estiver no cache (miss), busca no banco
        if notificacoes is None:
            notificacoes = Notificacao.objects.filter(usuario_destino=request.user, lida=False) # <- CORRIGIDO
            # Guarda o resultado no cache por 120 segundos (2 minutos)
            cache.set(cache_key, notificacoes, 120)

        return {'notificacoes_nao_lidas': notificacoes}
    return {}