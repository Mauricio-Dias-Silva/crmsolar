# financeiro/apps.py

from django.apps import AppConfig

class FinanceiroConfig(AppConfig): # <<< VERIFIQUE ESTE NOME DA CLASSE
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financeiro'
    verbose_name = 'Gestão Financeira e Audesp'

 