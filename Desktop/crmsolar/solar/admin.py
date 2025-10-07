from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Cliente, Projeto, Usuario, Departamento, MenuPermissao, 
    Proposta, 
    ProjetoExecutado,
)
from .forms import ClienteForm 
from django import forms
from django.db.models import F # Importe F se for usado para otimização


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
    form = ClienteForm 


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cliente', 'status', 'data_inicio', 'potencia_kwp', 'valor_total')
    list_filter = ('status', 'data_inicio', 'cliente', 'fornecedor')
    search_fields = ('nome', 'cliente__nome', 'descricao')
    date_hierarchy = 'data_inicio'
    raw_id_fields = ('cliente', 'fornecedor',)


@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    # Campos exibidos na lista (Funcionalidade de Rastreio)
    list_display = ('numero', 'cliente_nome', 'status_crm', 'potencia_kwp', 'valor_total', 'vendedor')
    search_fields = ('numero', 'cliente_nome', 'cpf_cnpj', 'vendedor')
    list_filter = ('status_crm', 'vendedor')

    fieldsets = (
        ('INFORMAÇÕES BÁSICAS DA PROPOSTA', {
            'fields': ('numero', 'vendedor', 'status_crm', 'data_validade')
        }),
        ('DADOS DO CLIENTE PARA RASTREIO', {
            'fields': ('cliente_nome', 'cpf_cnpj')
        }),
        ('DETALHES DO PROJETO', {
            'fields': ('potencia_kwp', 'valor_total')
        }),
    )


@admin.register(ProjetoExecutado)
class ProjetoExecutadoAdmin(admin.ModelAdmin):
    # Campos exibidos na lista (Portfólio)
    list_display = ('titulo', 'localidade', 'potencia_kwp', 'tipo_projeto', 'is_active')
    list_filter = ('tipo_projeto', 'localidade', 'is_active')
    search_fields = ('titulo', 'localidade')

    fieldsets = (
        (None, {
            'fields': ('titulo', 'localidade', 'tipo_projeto', 'is_active', 'imagem_capa')
        }),
        ('MÉTRICAS DO PROJETO', {
            'fields': ('potencia_kwp',)
        }),
    )


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(MenuPermissao)
class MenuPermissaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'rota')
    search_fields = ('nome', 'rota')