from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Cliente, Projeto, Usuario, Departamento, MenuPermissao,
    # 💡 Adicionei o ItemProposta aqui para podermos usá-lo
    ItemProposta,
    Portfolio, DocumentoProjeto
    # Removi Proposta e ProjetoExecutado se não estiverem nos seus models atuais
    # para evitar erros. Adicione-os de volta se eles existirem.
)
from .forms import ClienteForm

# --- INLINES: A "MÁGICA" PARA ADICIONAR ITENS DENTRO DO PROJETO ---
# Este é o conceito que você queria decorar para resolver problemas como este.

class ItemPropostaInline(admin.TabularInline):
    model = ItemProposta
    # Mostra 3 campos vazios para adicionar novos itens de uma vez
    extra = 3
    # Adiciona um cabeçalho mais amigável
    verbose_name_plural = "Itens do Orçamento (Equipamentos e Serviços)"

class DocumentoProjetoInline(admin.TabularInline):
    model = DocumentoProjeto
    extra = 1
    verbose_name_plural = "Documentos e Fotos do Projeto (para a proposta)"

# --- REGISTROS DO ADMIN ---

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    # Mantive sua configuração, só ajustei um campo que poderia estar faltando
    list_display = ('titulo', 'destaque')
    list_filter = ('destaque',)
    search_fields = ('titulo',)

# 💡 DocumentoProjeto não precisa mais ser registrado separadamente,
# pois agora ele é gerenciado dentro do Projeto.
# @admin.register(DocumentoProjeto) ... (REMOVIDO)

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    # Mantive sua configuração de Usuario exatamente como estava. Ótima!
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
    # Mantive sua configuração e adicionei a linha 'inlines'
    list_display = ('nome', 'cliente', 'status', 'data_inicio', 'potencia_kwp', 'valor_total')
    list_filter = ('status', 'data_inicio', 'cliente') # Removi 'fornecedor' para evitar erro se não existir
    search_fields = ('nome', 'cliente__nome', 'descricao')
    date_hierarchy = 'data_inicio'
    raw_id_fields = ('cliente',) # Removi 'fornecedor' para evitar erro se não existir

    # 💡 AQUI A MÁGICA ACONTECE!
    inlines = [ItemPropostaInline, DocumentoProjetoInline]

# Mantive seus outros registros do admin.
# Se Proposta e ProjetoExecutado não existirem no seu models.py,
# comente ou remova os blocos abaixo para evitar erros.

# @admin.register(Proposta) ...
# @admin.register(ProjetoExecutado) ...

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(MenuPermissao)
class MenuPermissaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'rota')
    search_fields = ('nome', 'rota')

