# ofertas/forms.py

from django import forms
from .models import Oferta, Categoria, Vendedor
from django.utils import timezone
from .models import Avaliacao

class OfertaForm(forms.ModelForm):
    # Campos que o vendedor poderá editar diretamente
    titulo = forms.CharField(label="Título da Oferta", max_length=255, 
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    descricao_detalhada = forms.CharField(label="Descrição Detalhada", 
                                          widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    preco_original = forms.DecimalField(label="Preço Original (R$)", max_digits=10, decimal_places=2, 
                                        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    preco_desconto = forms.DecimalField(label="Preço com Desconto (R$)", max_digits=10, decimal_places=2, 
                                        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    data_inicio = forms.DateTimeField(label="Data de Início", 
                                       widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    data_termino = forms.DateTimeField(label="Data de Término", 
                                        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    quantidade_minima_ativacao = forms.IntegerField(label="Qtd. Mínima para Ativação", min_value=1, 
                                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    quantidade_maxima_cupons = forms.IntegerField(label="Qtd. Máxima de Cupons (Opcional)", required=False, min_value=1, 
                                                  widget=forms.NumberInput(attrs={'class': 'form-control'}))
    imagem_principal = forms.ImageField(label="Imagem Principal da Oferta", required=False, 
                                        widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    # Campo para escolher a categoria (vendedor só pode escolher categorias ativas)
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(ativa=True).order_by('nome'),
        label="Categoria",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Oferta
        fields = [
            'titulo', 'descricao_detalhada', 'preco_original', 'preco_desconto', 
            'data_inicio', 'data_termino', 'quantidade_minima_ativacao', 
            'quantidade_maxima_cupons', 'imagem_principal', 'categoria'
        ]
        # Não incluímos 'vendedor', 'slug', 'publicada', 'status', 'quantidade_vendida', 'data_criacao', 'data_atualizacao'
        # pois esses campos serão definidos no backend ou automaticamente.

    def clean(self):
        cleaned_data = super().clean()
        preco_original = cleaned_data.get('preco_original')
        preco_desconto = cleaned_data.get('preco_desconto')
        data_inicio = cleaned_data.get('data_inicio')
        data_termino = cleaned_data.get('data_termino')

        if preco_original and preco_desconto and preco_desconto >= preco_original:
            self.add_error('preco_desconto', 'O preço com desconto deve ser menor que o preço original.')

        if data_inicio and data_termino:
            if data_inicio >= data_termino:
                self.add_error('data_termino', 'A data de término deve ser posterior à data de início.')
            if data_inicio < timezone.now() - timezone.timedelta(minutes=1): # Permite 1 minuto de tolerância
                # Apenas para novas ofertas, não para edição de ofertas antigas já iniciadas
                # Isso pode ser ajustado com lógica mais complexa na view para 'edit'
                if self.instance.pk is None: # Se for uma nova oferta
                    self.add_error('data_inicio', 'A data de início não pode ser no passado.')
        
        return cleaned_data



# ofertas/forms.py (adicione no final do arquivo)

# ... (Seu código existente do OfertaForm) ...

class AvaliacaoForm(forms.ModelForm):
    nota = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)], 
        label="Sua Nota (1-5)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comentario = forms.CharField(
        label="Seu Comentário (Opcional)", 
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        # 'oferta' e 'usuario' serão preenchidos na view