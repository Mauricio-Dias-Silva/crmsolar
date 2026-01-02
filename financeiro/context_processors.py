# core/context_processors.py
import datetime

def global_context(request):
    return {
        'logo_url': 'img/logo_barueri.jpg', # Caminho do seu logo
        'ano_atual': datetime.date.today().year, # Opcional: para o footer de direitos autorais
        # Adicione aqui outras variáveis que você queira que estejam em todos os templates
    }