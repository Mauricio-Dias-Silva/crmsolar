# SysGov_Project/core/context_processors.py
import datetime
from .models import Notificacao

def global_context(request):
    return {
        'logo_url': 'img/logo_barueri.jpg', # Caminho do seu logo
        'ano_atual': datetime.date.today().year, # Opcional: para o footer de direitos autorais
        # Adicione aqui outras variáveis que você queira que estejam em todos os templates
    }


def notificacoes_nao_lidas(request):
    """
    Este processador de contexto verifica se o utilizador está autenticado
    e, em caso afirmativo, busca as suas notificações não lidas.
    """
    if request.user.is_authenticated:
        # Busca todas as notificações do utilizador que ainda não foram lidas
        notificacoes = Notificacao.objects.filter(usuario_destino=request.user, lida=False)
        # Conta quantas são
        count_notificacoes = notificacoes.count()
        
        # Retorna um dicionário que será adicionado ao contexto de TODOS os templates
        return {
            'notificacoes_nao_lidas_list': notificacoes,
            'notificacoes_nao_lidas_count': count_notificacoes
        }
    # Se o utilizador não estiver logado, retorna um dicionário vazio
    return {}
