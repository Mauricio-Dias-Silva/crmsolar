# ofertas/models.py
from django.db import models
from django.utils import timezone 
from django.utils.text import slugify 

# Certifique-se que Vendedor e Categoria estão definidos ANTES desta classe
# ou importados corretamente se estiverem em outros apps.
# Pelo seu código anterior, eles estavam no mesmo arquivo, então não precisam ser importados aqui.

class Vendedor(models.Model):
    # Seu código do modelo Vendedor
    nome_empresa = models.CharField(max_length=200, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ (somente números)")
    email_contato = models.EmailField(verbose_name="Email de Contato")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição da Empresa")
    logo = models.ImageField(upload_to='vendedores/logos/', blank=True, null=True, verbose_name="Logo do Vendedor")
    endereco = models.CharField(max_length=255, verbose_name="Endereço Completo")
    ativo = models.BooleanField(default=True, verbose_name="Ativo no Site")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ['nome_empresa']

    def __str__(self):
        return self.nome_empresa

class Categoria(models.Model):
    # Seu código do modelo Categoria
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL amigável (gerado automaticamente ou manual)", blank=True)
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição da Categoria")
    ativa = models.BooleanField(default=True, verbose_name="Ativa no Site")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug: # Se o slug não estiver preenchido
            self.slug = slugify(self.nome) # Ele tenta gerar
        super().save(*args, **kwargs)


class Oferta(models.Model):
    # NOVO CAMPO: Tipo de Oferta
    TIPO_OFERTA_CHOICES = [
        ('unidade', 'Venda por Unidade (Imediata)'),
        ('lote', 'Compra Coletiva por Lote'),
    ]
    tipo_oferta = models.CharField(
        max_length=10, 
        choices=TIPO_OFERTA_CHOICES, 
        default='unidade', 
        verbose_name="Tipo de Oferta"
    )

    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='ofertas', verbose_name="Vendedor")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='ofertas', verbose_name="Categoria")
    titulo = models.CharField(max_length=255, verbose_name="Título da Oferta")
    imagem_principal = models.ImageField(upload_to='ofertas/imagens/', verbose_name="Imagem Principal da Oferta", blank=True, null=True) 
    slug = models.SlugField(max_length=255, unique=True, help_text="URL amigável da oferta", blank=True) 
    descricao_detalhada = models.TextField(verbose_name="Descrição Detalhada da Oferta")
    destaque = models.BooleanField(default=False, verbose_name="Oferta em Destaque")
    preco_original = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Original")
    preco_desconto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço com Desconto")
    data_inicio = models.DateTimeField(default=timezone.now, verbose_name="Data de Início da Oferta")
    data_termino = models.DateTimeField(verbose_name="Data de Término da Oferta")
    
    quantidade_minima_ativacao = models.IntegerField(default=1, verbose_name="Quantidade Mínima de Cupons para Ativação")
    quantidade_maxima_cupons = models.IntegerField(blank=True, null=True, verbose_name="Quantidade Máxima de Cupons (Limite)")
    
    quantidade_vendida = models.IntegerField(default=0, verbose_name="Quantidade de Cupons Vendidos")
    imagem_principal = models.ImageField(upload_to='ofertas/imagens/', verbose_name="Imagem Principal da Oferta")
    
    publicada = models.BooleanField(default=False, verbose_name="Publicada (Visível no Site)")

    # Status da Oferta (para controle interno e exibição)
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('ativa', 'Ativa'),
        ('sucesso', 'Sucesso (mínimo atingido)'),
        ('expirada', 'Expirada'),
        ('cancelada', 'Cancelada'),
        ('falha_lote', 'Falha (mínimo não atingido)'), # NOVO STATUS
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status da Oferta")

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"
        ordering = ['-data_inicio'] 

    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    @property
    def percentual_desconto(self):
        if self.preco_original > 0:
            return f"{((self.preco_original - self.preco_desconto) / self.preco_original) * 100:.0f}%"
        return "0%"

    @property
    def esta_expirada(self):
        return timezone.now() > self.data_termino

    @property
    def esta_disponivel_para_compra(self):
        # Para ofertas por unidade: deve estar ativa e dentro do limite
        if self.tipo_oferta == 'unidade':
            return self.publicada and self.status == 'ativa' and not self.esta_expirada and \
                   (self.quantidade_maxima_cupons is None or self.quantidade_vendida < self.quantidade_maxima_cupons)
        # Para ofertas por lote: deve estar ativa e dentro do prazo, mas não "falha" ainda
        elif self.tipo_oferta == 'lote':
            return self.publicada and self.status == 'ativa' and not self.esta_expirada and \
                   (self.quantidade_maxima_cupons is None or self.quantidade_vendida < self.quantidade_maxima_cupons)
        return False # Outros tipos/status não estão disponíveis para compra

    # Novo método para verificar e concretizar/falhar lotes (chamado por tarefa agendada)
    def verificar_lote_e_finalizar(self):
        if self.tipo_oferta == 'lote' and self.status == 'ativa' and self.esta_expirada:
            if self.quantidade_vendida >= self.quantidade_minima_ativacao:
                self.status = 'sucesso'
                print(f"LOTE SUCESSO: Oferta '{self.titulo}' atingiu o mínimo. Processar capturas e cupons.")
            else:
                self.status = 'falha_lote'
                print(f"LOTE FALHA: Oferta '{self.titulo}' NÃO atingiu o mínimo. Processar estornos.")
            self.save()

# (Seu modelo Avaliacao deve vir AQUI, após o Oferta, para evitar NameError)
class Avaliacao(models.Model):
    # ... (Seu código do modelo Avaliacao) ...
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='avaliacoes', verbose_name="Oferta Avaliada")
    usuario = models.ForeignKey('contas.Usuario', on_delete=models.CASCADE, related_name='minhas_avaliacoes', verbose_name="Usuário Avaliador")
    nota = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Nota (1-5)") # Notas de 1 a 5
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentário")
    data_avaliacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Avaliação")

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        unique_together = ('oferta', 'usuario') # Um usuário só pode avaliar a mesma oferta uma vez
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f"Avaliação de {self.usuario.username} para {self.oferta.titulo} - Nota: {self.nota}"