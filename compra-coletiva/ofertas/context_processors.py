# ofertas/context_processors.py

from .models import Categoria

def categorias_globais(request):
    """
    Adiciona todas as categorias ao contexto de cada requisição.
    """
    return {'categorias': Categoria.objects.all().order_by('nome')}