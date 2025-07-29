# populate_data.py

import os
import django
from django.conf import settings
from django.apps import apps

# Configura a variável de ambiente para as configurações do seu projeto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_compra_coletiva.settings')

# Inicializa o Django
django.setup()

# Importações do seu script original
from ofertas.models import Vendedor, Categoria, Oferta
from contas.models import Usuario
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify
import requests
from django.core.files.base import ContentFile
from io import BytesIO # Certifique-se que BytesIO é importado

print("--- Iniciando Criação de Dados Fictícios ---")

# --- Funções Auxiliares ---
def get_image_from_url(url, filename):
    """Baixa uma imagem de uma URL e retorna como ContentFile."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # Lança um erro para status HTTP ruins
        # Usar BytesIO para compatibilidade com ContentFile
        from io import BytesIO
        buffer = BytesIO(response.content)
        return ContentFile(buffer.getvalue(), name=filename)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar imagem '{url}': {e}. Usando placeholder se possível.")
        return None # Retorna None se o download falhar

# --- 1. Criar Vendedores ---
print("\n1. Criando Vendedores...")
vendedores_data = [
    {'nome': 'MegaDescontos Ltda', 'cnpj': '00000000000101', 'email': 'contato@megadescontos.com', 'end': 'Av. Principal, 100'},
    {'nome': 'Ofertas Incríveis S.A.', 'cnpj': '00000000000202', 'email': 'falecom@ofertasincriveis.com', 'end': 'Rua Secundária, 50'},
    {'nome': 'Barganha Total Eireli', 'cnpj': '00000000000303', 'email': 'suporte@barganhatotal.com', 'end': 'Travessa dos Sonhos, 20'},
]
lista_vendedores = []
for vd in vendedores_data:
    vendedor, created = Vendedor.objects.get_or_create(
        cnpj=vd['cnpj'], # Usa CNPJ como identificador único para get_or_create
        defaults={
            'nome_empresa': vd['nome'],
            'email_contato': vd['email'],
            'endereco': vd['end'],
            'telefone': '99999-8888',
            'descricao': f"Empresa especializada em {vd['nome']}."
        }
    )
    if created:
        print(f"  Vendedor '{vendedor.nome_empresa}' criado.")
    else:
        print(f"  Vendedor '{vendedor.nome_empresa}' já existe.")
    lista_vendedores.append(vendedor)

# --- 2. Criar Categorias ---
print("\n2. Criando Categorias...")
categorias_data = [
    {'nome': 'Gastronomia', 'desc': 'Melhores restaurantes e bares da cidade.'},
    {'nome': 'Beleza e Bem-Estar', 'desc': 'Serviços de estética, spas e salões.'},
    {'nome': 'Viagens e Lazer', 'desc': 'Pacotes de viagens e atividades de lazer.'},
    {'nome': 'Produtos Eletrônicos', 'desc': 'Eletrônicos com super descontos.'},
    {'nome': 'Esportes e Fitness', 'desc': 'Academias, equipamentos e atividades esportivas.'},
]
lista_categorias = []
for cat in categorias_data:
    categoria, created = Categoria.objects.get_or_create(
        slug=slugify(cat['nome']), # Usa slug como identificador único
        defaults={'nome': cat['nome'], 'descricao': cat['desc']}
    )
    if created:
        print(f"  Categoria '{categoria.nome}' criada.")
    else:
        print(f"  Categoria '{categoria.nome}' já existe.")
    lista_categorias.append(categoria)

# --- 3. Criar Ofertas Variadas ---
print("\n3. Criando Ofertas...")

ofertas_data = [
    # Ofertas por Unidade (Imediata)
    {
        'titulo': 'Jantar Romântico para Dois', 'vendedor': lista_vendedores[0], 'categoria': lista_categorias[0],
        'descricao': 'Menu completo com entrada, prato principal e sobremesa.', 'original': 200.00, 'desconto': 99.90,
        'inicio_dias': 0, 'termino_dias': 7, 'min_ativ': 1, 'max_cupons': 50, 'destaque': True, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/jantar/300/200'
    },
    {
        'titulo': 'Massagem Relaxante 1h', 'vendedor': lista_vendedores[1], 'categoria': lista_categorias[1],
        'descricao': 'Sessão de massagem relaxante com óleos essenciais.', 'original': 120.00, 'desconto': 49.90,
        'inicio_dias': 0, 'termino_dias': 10, 'min_ativ': 1, 'max_cupons': 30, 'destaque': True, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/massagem/300/200'
    },
    {
        'titulo': 'Pacote de Fotos Profissionais', 'vendedor': lista_vendedores[2], 'categoria': lista_categorias[2],
        'descricao': 'Sessão de fotos com 10 fotos editadas e impressas.', 'original': 350.00, 'desconto': 149.90,
        'inicio_dias': 0, 'termino_dias': 15, 'min_ativ': 1, 'max_cupons': 20, 'destaque': False, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/fotografo/300/200'
    },
    {
        'titulo': 'Fone de Ouvido Bluetooth Premium', 'vendedor': lista_vendedores[0], 'categoria': lista_categorias[3],
        'descricao': 'Áudio de alta qualidade e bateria de longa duração.', 'original': 250.00, 'desconto': 125.00,
        'inicio_dias': 0, 'termino_dias': 5, 'min_ativ': 1, 'max_cupons': 100, 'destaque': False, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/fone/300/200'
    },
    {
        'titulo': 'Mês de Pilates Completo', 'vendedor': lista_vendedores[1], 'categoria': lista_categorias[4],
        'descricao': 'Aulas de pilates em estúdio moderno, todas as modalidades.', 'original': 180.00, 'desconto': 89.90,
        'inicio_dias': 0, 'termino_dias': 20, 'min_ativ': 1, 'max_cupons': 40, 'destaque': False, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/pilates/300/200'
    },
    # Ofertas por Lote (Compra Coletiva)
    {
        'titulo': 'Cesta de Produtos Orgânicos (Lote)', 'vendedor': lista_vendedores[2], 'categoria': lista_categorias[0],
        'descricao': 'Cesta variada de frutas e vegetais orgânicos da estação.', 'original': 100.00, 'desconto': 60.00,
        'inicio_dias': 0, 'termino_minutos': 15, 'min_ativ': 3, 'max_cupons': 10, 'destaque': True, 'tipo': 'lote',
        'img_url': 'https://picsum.photos/seed/organicos/300/200'
    },
    {
        'titulo': 'Kit de Skincare Vegano (Lote)', 'vendedor': lista_vendedores[0], 'categoria': lista_categorias[1],
        'descricao': 'Produtos veganos para uma pele saudável e hidratada.', 'original': 150.00, 'desconto': 75.00,
        'inicio_dias': 0, 'termino_minutos': 30, 'min_ativ': 5, 'max_cupons': 15, 'destaque': False, 'tipo': 'lote',
        'img_url': 'https://picsum.photos/seed/skincare/300/200'
    },
    {
        'titulo': 'Viagem para Praia - Fim de Semana (Lote)', 'vendedor': lista_vendedores[1], 'categoria': lista_categorias[2],
        'descricao': 'Pacote para duas pessoas com hospedagem e café da manhã.', 'original': 800.00, 'desconto': 400.00,
        'inicio_dias': 0, 'termino_horas': 2, 'min_ativ': 2, 'max_cupons': 5, 'destaque': True, 'tipo': 'lote',
        'img_url': 'https://picsum.photos/seed/praia/300/200'
    },
    {
        'titulo': 'Assinatura de Streaming Anual (Lote)', 'vendedor': lista_vendedores[2], 'categoria': lista_categorias[3],
        'descricao': 'Acesso ilimitado a filmes e séries por um ano.', 'original': 180.00, 'desconto': 90.00,
        'inicio_dias': 0, 'termino_horas': 3, 'min_ativ': 7, 'max_cupons': 20, 'destaque': False, 'tipo': 'lote',
        'img_url': 'https://picsum.photos/seed/streaming/300/200'
    },
    {
        'titulo': 'Aulas de Natação Pacote Mensal (Lote)', 'vendedor': lista_vendedores[0], 'categoria': lista_categorias[4],
        'descricao': 'Aulas de natação para todas as idades, piscina aquecida.', 'original': 140.00, 'desconto': 70.00,
        'inicio_dias': 0, 'termino_horas': 1, 'min_ativ': 4, 'max_cupons': 12, 'destaque': False, 'tipo': 'lote',
        'img_url': 'https://picsum.photos/seed/natacao/300/200'
    },
    # Mais algumas ofertas variadas para preencher (mix de tipos e destaques)
    {
        'titulo': 'Corte de Cabelo e Hidratação', 'vendedor': lista_vendedores[1], 'categoria': lista_categorias[1],
        'descricao': 'Serviço completo de cabeleireiro para renovar seu visual.', 'original': 100.00, 'desconto': 49.90,
        'inicio_dias': 0, 'termino_dias': 5, 'min_ativ': 1, 'max_cupons': 30, 'destaque': False, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/corte/300/200'
    },
    {
        'titulo': 'Curso Online de Fotografia (Lote)', 'vendedor': lista_vendedores[2], 'categoria': lista_categorias[2],
        'descricao': 'Aprenda técnicas de fotografia com aulas gravadas e ao vivo.', 'original': 200.00, 'desconto': 100.00,
        'inicio_dias': 0, 'termino_horas': 4, 'min_ativ': 8, 'max_cupons': 25, 'destaque': True, 'tipo': 'lote',
        'img_url': 'https://picsum.photos/seed/fotografia/300/200'
    },
    {
        'titulo': 'Tablet 10 polegadas', 'vendedor': lista_vendedores[0], 'categoria': lista_categorias[3],
        'descricao': 'Tablet rápido e com tela grande para trabalho e lazer.', 'original': 900.00, 'desconto': 450.00,
        'inicio_dias': 0, 'termino_dias': 10, 'min_ativ': 1, 'max_cupons': 50, 'destaque': False, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/tablet/300/200'
    },
    {
        'titulo': 'Kit de Higiene Pet (Lote)', 'vendedor': lista_vendedores[1], 'categoria': lista_categorias[4],
        'descricao': 'Shampoo, condicionador e escova para seu melhor amigo.', 'original': 70.00, 'desconto': 35.00,
        'inicio_dias': 0, 'termino_minutos': 20, 'min_ativ': 6, 'max_cupons': 18, 'destaque': False, 'tipo': 'lote',
        'img_url': 'https://picsum.photos/seed/pet/300/200'
    },
    {
        'titulo': 'Assinatura Academia Mensal', 'vendedor': lista_vendedores[2], 'categoria': lista_categorias[4],
        'descricao': 'Acesso total a todas as áreas e aulas da academia.', 'original': 130.00, 'desconto': 65.00,
        'inicio_dias': 0, 'termino_dias': 30, 'min_ativ': 1, 'max_cupons': 100, 'destaque': True, 'tipo': 'unidade',
        'img_url': 'https://picsum.photos/seed/academia/300/200'
    },
]

for i, oferta_data in enumerate(ofertas_data):
    # Calcula as datas de inicio e termino
    start_time = timezone.now() + timedelta(days=oferta_data.get('inicio_dias', 0))
    end_time = start_time + timedelta(
        days=oferta_data.get('termino_dias', 0),
        hours=oferta_data.get('termino_horas', 0),
        minutes=oferta_data.get('termino_minutos', 0)
    )
    
    # Baixa a imagem se a URL estiver presente
    img_file = None
    if 'img_url' in oferta_data:
        # Tenta baixar a imagem. Se falhar, img_file será None e o Django usará um placeholder.
        img_file = get_image_from_url(oferta_data['img_url'], f"oferta_{i}.jpg")

    oferta, created = Oferta.objects.get_or_create(
        slug=slugify(oferta_data['titulo']), # Usa slug como identificador único
        defaults={
            'titulo': oferta_data['titulo'],
            'vendedor': oferta_data['vendedor'],
            'categoria': oferta_data['categoria'],
            'descricao_detalhada': oferta_data['descricao'],
            'preco_original': oferta_data['original'],
            'preco_desconto': oferta_data['desconto'],
            'data_inicio': start_time,
            'data_termino': end_time,
            'quantidade_minima_ativacao': oferta_data['min_ativ'],
            'quantidade_maxima_cupons': oferta_data['max_cupons'],
            'imagem_principal': img_file, # Define a imagem baixada
            'publicada': True, # Já publicamos para que apareça
            'status': 'ativa', # Status inicial para a maioria
            'destaque': oferta_data['destaque'],
            'tipo_oferta': oferta_data['tipo']
        }
    )
    if created:
        print(f"  Oferta '{oferta.titulo}' ({oferta.get_tipo_oferta_display()}) criada.")
    else:
        print(f"  Oferta '{oferta.titulo}' já existe.")

# --- 4. Associar o superusuário a um Vendedor para o Painel ---
print("\n4. Associando superusuário a um vendedor (se possível)...")
try:
    admin_user = Usuario.objects.filter(is_superuser=True).first()
    if admin_user and not admin_user.vendedor:
        admin_user.vendedor = lista_vendedores[0] # Associa ao primeiro vendedor
        admin_user.save()
        print(f"  Superusuário '{admin_user.username}' associado a '{lista_vendedores[0].nome_empresa}'.")
    elif admin_user and admin_user.vendedor:
        print(f"  Superusuário '{admin_user.username}' já está associado a '{admin_user.vendedor.nome_empresa}'.")
    else:
        print("  Nenhum superusuário encontrado para associar a um vendedor.")
except Exception as e:
    print(f"  Erro ao tentar associar superusuário a vendedor: {e}")

print("\n--- Criação de Dados Fictícios Concluída! ---")