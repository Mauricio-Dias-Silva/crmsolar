# contas/models.py (adicione no final do arquivo)

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, Group, Permission

from ofertas.models import Vendedor 


class Usuario(AbstractUser):
    # ... (Seu código existente do modelo Usuario) ...
    # Garanta que o OneToOneField para Vendedor está aqui
    vendedor = models.OneToOneField(
        Vendedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='usuario_associado',
        verbose_name="Vendedor Associado"
    )
    # E que os ManyToManyFields para Group e Permission estão aqui
    groups = models.ManyToManyField(
        Group, 
        verbose_name=('groups'),
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their their groups.'),
        related_name="contas_usuario_set", 
        related_query_name="contas_usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission, 
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="contas_usuario_permissions", 
        related_query_name="contas_usuario_permission",
    )

    class Meta(AbstractUser.Meta): 
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.username 
    
    @property
    def eh_vendedor_ou_associado(self):
        return self.vendedor is not None and self.vendedor.status_aprovacao == 'aprovado'


class Notificacao(models.Model):
    TIPOS_NOTIFICACAO = [
        ('sistema', 'Sistema'),
        ('compra', 'Compra'),
        ('lote', 'Lote'),
        ('vendedor', 'Vendedor'),
        ('cupom', 'Cupom'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificacoes', verbose_name="Usuário")
    titulo = models.CharField(max_length=255, verbose_name="Título")
    mensagem = models.TextField(verbose_name="Mensagem")
    tipo = models.CharField(max_length=20, choices=TIPOS_NOTIFICACAO, default='sistema', verbose_name="Tipo")
    lida = models.BooleanField(default=False, verbose_name="Lida")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    url_destino = models.URLField(max_length=200, blank=True, null=True, verbose_name="URL de Destino")

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Notificação para {self.usuario.username}: {self.titulo[:50]}..."
    

# contas/models.py (adicione no final do arquivo, após o modelo Notificacao)



def criar_notificacao(usuario, titulo, mensagem, tipo='sistema', url_destino=None):
    """Cria e salva uma nova notificação para um usuário."""
    with transaction.atomic():
        Notificacao.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            url_destino=url_destino
        )