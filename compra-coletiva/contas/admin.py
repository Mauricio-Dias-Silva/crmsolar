# contas/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import Usuario, Notificacao


# Se você está usando o padrão sem CustomUserAdmin explícito, este é o registro
if admin.site.is_registered(Usuario): 
    admin.site.unregister(Usuario) 

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    # CORREÇÃO AQUI: Garante que o fieldset 'Associação Vendedor' seja adicionado corretamente.
    # O fieldsets deve ser uma lista de tuplas. Cada tupla contém (Título, Dicionário de opções).
    # O Dicionário de opções geralmente contém uma lista de campos (ou outra estrutura de layout).
    fieldsets = UserAdmin.fieldsets + (
        ('Associação Vendedor', {'fields': ('vendedor',)}), # <--- CORRIGIDO AQUI!
    )
    list_display = UserAdmin.list_display + ('vendedor', 'eh_vendedor_ou_associado')
    list_filter = UserAdmin.list_filter + ('vendedor__status_aprovacao',)


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo', 'tipo', 'lida', 'data_criacao')
    list_filter = ('tipo', 'lida')
    search_fields = ('usuario__username', 'titulo', 'mensagem')
    raw_id_fields = ('usuario',) 
    actions = ['marcar_como_lida', 'marcar_como_nao_lida']

    @admin.action(description='Marcar notificações como lidas')
    def marcar_como_lida(self, request, queryset):
        updated = queryset.update(lida=True)
        self.message_user(request, f'{updated} notificações marcadas como lidas.')
    
    @admin.action(description='Marcar notificações como não lidas')
    def marcar_como_nao_lida(self, request, queryset):
        updated = queryset.update(lida=False)
        self.message_user(request, f'{updated} notificações marcadas como não lidas.')