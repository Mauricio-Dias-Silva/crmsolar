# SysGov_Project/integracao_audesp/admin.py

from django.contrib import admin
from .models import AudespConfiguracao, SubmissaoAudesp

@admin.register(AudespConfiguracao)
class AudespConfiguracaoAdmin(admin.ModelAdmin):
    list_display = ('municipio_codigo_audesp', 'entidade_codigo_audesp')

@admin.register(SubmissaoAudesp)
class SubmissaoAudespAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'documento_submetido', 'status_tce', 'data_submissao', 'usuario_responsavel')
    list_filter = ('status_tce', 'content_type')
    search_fields = ('protocolo_tce', 'documento_submetido__id')
    readonly_fields = ('documento_submetido',) # Torna o GFK apenas de leitura no admin