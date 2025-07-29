# pedidos_coletivos/apps.py

from django.apps import AppConfig

class PedidosColetivosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pedidos_coletivos'
    verbose_name = 'Pedidos Coletivos'

    def ready(self):
        # Importa os signals quando o app está pronto
        # Isso garante que a criação do CreditoUsuario para novos usuários funcione
        import pedidos_coletivos.signals