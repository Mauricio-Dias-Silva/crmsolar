# ofertas/models.py

from django.db import models
from django.utils import timezone 
from django.utils.text import slugify 
from django.urls import reverse # <--- ADICIONADO: Para get_absolute_url


# === Modelo Vendedor ===
class Vendedor(models.Model):
    STATUS_APROVACAO_CHOICES = [
        ('pendente', 'Pendente de Aprovação'),
        ('aprovado', 'Aprovado'),
        ('suspenso', 'Suspenso'),
        ('rejeitado', 'Rejeitado'),
    ]
    nome_empresa = models.CharField(max_length=200, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ (somente números)")
    email_contato = models.EmailField(verbose_name="Email de Contato")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição da Empresa")
    logo = models.ImageField(upload_to='vendedores/logos/', blank=True, null=True, verbose_name="Logo do Vendedor")
    endereco = models.CharField(max_length=255, verbose_name="Endereço Completo")
    ativo = models.BooleanField(default=True, verbose_name="Ativo no Site") 
    
    status_aprovacao = models.CharField(
        max_length=10, 
        choices=STATUS_APROVACAO_CHOICES, 
        default='pendente', 
        verbose_name="Status de Aprovação"
    )

    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"
        ordering = ['nome_empresa']

    def __str__(self):
        return self.nome_empresa


# === Modelo Categoria ===
class Categoria(models.Model):
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


# === Modelo Oferta ===
class Oferta(models.Model):
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
    # IMAGEM PRINCIPAL: Apenas uma declaração do campo
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
    
    publicada = models.BooleanField(default=False, verbose_name="Publicada (Visível no Site)")

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('ativa', 'Ativa'),
        ('sucesso', 'Sucesso (mínimo atingido)'),
        ('expirada', 'Expirada'),
        ('cancelada', 'Cancelada'),
        ('falha_lote', 'Falha (mínimo não atingido)'), 
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
        if self.tipo_oferta == 'unidade':
            return self.publicada and self.status == 'ativa' and not self.esta_expirada and \
                   (self.quantidade_maxima_cupons is None or self.quantidade_vendida < self.quantidade_maxima_cupons)
        elif self.tipo_oferta == 'lote':
            return self.publicada and self.status == 'ativa' and not self.esta_expirada and \
                   (self.quantidade_maxima_cupons is None or self.quantidade_vendida < self.quantidade_maxima_cupons)
        return False

    def verificar_lote_e_finalizar(self):
        if self.tipo_oferta == 'lote' and self.status == 'ativa' and self.esta_expirada:
            if self.quantidade_vendida >= self.quantidade_minima_ativacao:
                self.status = 'sucesso'
                print(f"LOTE SUCESSO: Oferta '{self.titulo}' atingiu o mínimo. Processar capturas e cupons.")
            else:
                self.status = 'falha_lote'
                print(f"LOTE FALHA: Oferta '{self.titulo}' NÃO atingiu o mínimo. Processar estornos.")
            self.save()

    # MÉTODO PARA SEO E NOTIFICAÇÕES (get_absolute_url)
    def get_absolute_url(self):
        return reverse('ofertas:detalhe_oferta', kwargs={'slug_oferta': self.slug})


# === Modelo Avaliacao ===
class Avaliacao(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, related_name='avaliacoes', verbose_name="Oferta Avaliada")
    usuario = models.ForeignKey('contas.Usuario', on_delete=models.CASCADE, related_name='minhas_avaliacoes', verbose_name="Usuário Avaliador")
    nota = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Nota (1-5)") 
    comentario = models.TextField(blank=True, null=True, verbose_name="Comentário")
    data_avaliacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Avaliação")

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        unique_together = ('oferta', 'usuario') 
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f"Avaliação de {self.usuario.username} para {self.oferta.titulo} - Nota: {self.nota}"


# === Modelo Banner ===
class Banner(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título do Banner")
    imagem = models.ImageField(upload_to='banners/', verbose_name="Imagem do Banner")
    url_destino = models.URLField(max_length=200, blank=True, null=True, verbose_name="URL de Destino")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem = models.IntegerField(default=0, verbose_name="Ordem de Exibição")

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['ordem']

    def __str__(self):
        return self.titulo