# contas/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from ofertas.models import Vendedor # Adicione esta linha


class Usuario(AbstractUser):
    # Seus campos personalizados, se houver, como telefone, endereço, etc.
    # Exemplo:
    # telefone = models.CharField(max_length=15, blank=True, null=True)

    # Adicione estes campos com 'related_name' para resolver o conflito
    # Importante: O related_name deve ser único para este modelo
    groups = models.ManyToManyField(
        Group, # Use o modelo Group importado
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their their groups.'
        ),
        related_name="contas_usuario_set", # <-- Nome único para o related_name de groups
        related_query_name="contas_usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission, # Use o modelo Permission importado
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="contas_usuario_permissions", # <-- Nome único para o related_name de user_permissions
        related_query_name="contas_usuario_permission",
    )
    
    # Campo adicionado para relacionar o Usuário a um Vendedor
    vendedor = models.ForeignKey(
        Vendedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='usuarios_associados',
        verbose_name="Vendedor Associado"
    )

    # A CLASSE META DEVE ESTAR DENTRO DA CLASSE USUARIO E CORRETAMENTE INDENTADA
    class Meta(AbstractUser.Meta): # É uma boa prática herdar de AbstractUser.Meta para manter padrões
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        # ordering = ['username'] # Exemplo: você pode adicionar ordenação padrão aqui

    # O MÉTODO __str__ DEVE ESTAR DENTRO DA CLASSE USUARIO E CORRETAMENTE INDENTADO
    def __str__(self):
        # O AbstractUser já tem um campo 'username', que é uma boa escolha aqui.
        return self.username 
    
    # A PROPRIEDADE DEVE ESTAR DENTRO DA CLASSE USUARIO E CORRETAMENTE INDENTADA
    @property
    def eh_vendedor_ou_associado(self):
        return self.vendedor is not None