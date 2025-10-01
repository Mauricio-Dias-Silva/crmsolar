from django.contrib import admin
from .models import Cliente, Projeto, Usuario, Departamento, MenuPermissao
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .forms import ClienteForm # Importa ClienteForm

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email', 'departamento', 'permissoes_menu')}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_crm_staff', 'is_customer', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_crm_staff', 'is_customer', 'is_staff', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_crm_staff', 'is_customer', 'departamento', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions', 'permissoes_menu')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'usuario')
    search_fields = ('nome', 'email', 'usuario__username', 'cpf', 'cnpj')
    # REMOVIDO: O `fields` duplicado que estava causando o erro
    # O ClienteForm já define os campos, então não precisamos deles aqui.
    form = ClienteForm # Usa o ClienteForm customizado
    
@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'status', 'data_inicio', 'data_fim', 'potencia_kwp', 'valor_total')
    list_filter = ('status', 'data_inicio', 'data_fim', 'cliente', 'fornecedor')
    search_fields = ('nome', 'cliente__nome', 'descricao')
    date_hierarchy = 'data_inicio'
    raw_id_fields = ('cliente', 'fornecedor',)

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(MenuPermissao)
class MenuPermissaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'rota')
    search_fields = ('nome', 'rota')
