# contas/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Importe UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Se você adicionar campos extras em Usuario, pode personalizá-los aqui
    pass