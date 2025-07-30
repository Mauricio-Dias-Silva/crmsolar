# contas/context_processors.py

from .models import Notificacao # Importe o modelo Notificacao

def notificacoes_nao_lidas_globais(request):
    """
    Adiciona a contagem de notificações não lidas ao contexto de cada requisição.
    """
    if request.user.is_authenticated:
        count = Notificacao.objects.filter(usuario=request.user, lida=False).count()
        return {'notificacoes_nao_lidas': count}
    return {'notificacoes_nao_lidas': 0}