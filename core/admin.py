# SysGov_Project/core/admin.py

from django.contrib import admin
# Remova EstudoTecnicoPreliminar e TermoDeReferencia da importação
from .models import Processo,ArquivoAnexo,Fornecedor

admin.site.register(Processo)
# Remova estas linhas:
# admin.site.register(EstudoTecnicoPreliminar)
# admin.site.register(TermoDeReferencia)
admin.site.register(Fornecedor)
admin.site.register(ArquivoAnexo)