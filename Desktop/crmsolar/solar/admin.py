from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Cliente, Projeto, Usuario, Departamento, MenuPermissao, Proposta, ProjetoExecutado,
    ItemProposta, Portfolio, DocumentoProjeto
   
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

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(MenuPermissao)
class MenuPermissaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'rota')
    search_fields = ('nome', 'rota')

@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'projeto', 'cliente_nome', 'valor_total', 'status_crm')
    list_filter = ('status_crm',)
    search_fields = ('numero', 'cliente_nome', 'projeto__nome')
    # Estes campos serão preenchidos sozinhos, então deixamos como "apenas leitura"
    readonly_fields = ('numero', 'cliente_nome', 'cpf_cnpj', 'potencia_kwp', 'valor_total')
    
    # Organiza o formulário para ficar mais limpo
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('projeto', 'vendedor', 'status_crm', 'data_validade')
        }),
        ('Dados Gerados Automaticamente', {
            'fields': ('numero', 'cliente_nome', 'cpf_cnpj', 'potencia_kwp', 'valor_total')
        }),
    )

@admin.register(ProjetoExecutado)
class ProjetoExecutadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'localidade', 'potencia_kwp', 'tipo_projeto', 'is_active')
    list_filter = ('tipo_projeto', 'is_active')
    search_fields = ('titulo', 'localidade')
