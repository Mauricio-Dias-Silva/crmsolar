# populate_data.py

import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker
from django.utils.text import slugify

# Configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_compra_coletiva.settings')
django.setup()

# Importar modelos APÓS o django.setup()
from django.contrib.auth import get_user_model
from ofertas.models import Vendedor, Categoria, Oferta
from pedidos_coletivos.models import PedidoColetivo, CreditoUsuario
from compras.models import Compra, Cupom
from contas.models import Notificacao

from django.db import transaction
from django.core.files.base import ContentFile
import requests
from django.urls import reverse # Necessário para o reverse no final do script

User = get_user_model()
fake = Faker('pt_BR') # Faker para dados aleatórios em português

def get_image_from_url(url, filename):
    """Baixa uma imagem de uma URL e retorna como ContentFile."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        from io import BytesIO
        buffer = BytesIO(response.content)
        return ContentFile(buffer.getvalue(), name=filename)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar imagem '{url}': {e}. Usando placeholder se possível.")
        return None

def clear_db():
    print("--- Iniciando limpeza completa do banco de dados ---")
    # Ordem de deleção é crucial devido a chaves estrangeiras
    Cupom.objects.all().delete()
    Compra.objects.all().delete()
    PedidoColetivo.objects.all().delete()
    Oferta.objects.all().delete()
    Vendedor.objects.all().delete()
    Categoria.objects.all().delete()
    Notificacao.objects.all().delete()
    # Não deletar CreditoUsuario diretamente se for OneToOne com User e o User for Superuser,
    # Mas se você limpou todos os usuários não-superuser, os CreditoUsuario associados também serão removidos.
    # Se precisar de limpeza explícita de CreditoUsuario que não sejam do superuser:
    CreditoUsuario.objects.exclude(usuario__is_superuser=True).delete()
    User.objects.filter(is_superuser=False).delete() # Não deletar superusuários existentes
    
    print("Banco de dados limpo.")
    print("--- Fim da limpeza ---")

def populate_data():
    print("\n--- Iniciando população de dados para o VarejoUnido ---")

    # --- Superusuário (se não existir) ---
    try:
        admin_user = User.objects.get(username='admin')
        print("Superusuário 'admin' já existe.")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser('admin', 'admin@varejounido.com', 'adminpass')
        print("Superusuário 'admin' criado.")

    # --- Usuários Compradores ---
    users_compradores = []
    print("Criando 15 usuários compradores...")
    for i in range(1, 16):
        user, created = User.objects.get_or_create( # Usar get_or_create para compradores
            username=f'comprador_{i}',
            defaults={
                'email': f'comprador_{i}@{fake.domain_name()}',
                'password': '123'
            }
        )
        users_compradores.append(user)
        # Garante que cada usuário comprador tenha um objeto CreditoUsuario
        CreditoUsuario.objects.get_or_create(usuario=user)
    print(f"Total de {len(users_compradores)} usuários compradores criados.")

    # --- Vendedores e Usuários Vendedores ---
    lista_vendedores = []
    print("\nCriando 5 vendedores (e seus usuários associados)...")
    vendedores_data = [
        {'nome_empresa': 'MegaDescontos Ltda', 'cnpj': '00000000000101', 'email_contato': 'contato@megadescontos.com', 'end': 'Av. Principal, 100'},
        {'nome_empresa': 'Ofertas Incríveis S.A.', 'cnpj': '00000000000202', 'email_contato': 'falecom@ofertasincriveis.com', 'end': 'Rua Secundária, 50'},
        {'nome_empresa': 'Barganha Total Eireli', 'cnpj': '00000000000303', 'email_contato': 'suporte@barganhatotal.com', 'end': 'Travessa dos Sonhos, 20'},
        {'nome_empresa': 'EconoMix Marketplace', 'cnpj': '00000000000404', 'email_contato': 'parceria@economix.com', 'end': 'Rua da Inovação, 77'},
        {'nome_empresa': 'Desconto Certo Ltda.', 'cnpj': '00000000000505', 'email_contato': 'admin@descontocerto.com', 'end': 'Alameda das Oportunidades, 10'},
    ]

    for i, vd in enumerate(vendedores_data):
        vendedor, created_vendedor = Vendedor.objects.get_or_create(
            cnpj=vd['cnpj'],
            defaults={
                'nome_empresa': vd['nome_empresa'],
                'email_contato': vd['email_contato'],
                'endereco': vd['end'],
                'telefone': fake.phone_number()[:15],
                'descricao': f"Empresa especializada em {vd['nome_empresa'].split(' ')[0].lower()}."
            }
        )
        if created_vendedor:
            print(f"  Vendedor '{vendedor.nome_empresa}' criado.")
        else:
            print(f"  Vendedor '{vendedor.nome_empresa}' já existe.")
        
        if i == 0: # Primeiro vendedor será o admin_user
            user_vendedor = admin_user
            user_vendedor.vendedor = vendedor
            user_vendedor.save()
            print(f"  Superusuário '{user_vendedor.username}' associado a '{vendedor.nome_empresa}'.")
            vendedor.status_aprovacao = 'aprovado'
            vendedor.save()
        else: # Outros vendedores terão usuários dedicados
            username = slugify(vd['nome_empresa']) + str(random.randint(100,999))
            user_vendedor, created_user_vendedor = User.objects.get_or_create(
                username=username,
                defaults={'email': vd['email_contato'], 'password': '123'}
            )
            user_vendedor.vendedor = vendedor
            user_vendedor.save()
            
            if created_user_vendedor:
                print(f"  Usuário '{user_vendedor.username}' criado e associado a '{vendedor.nome_empresa}'.")
            else:
                print(f"  Usuário '{user_vendedor.username}' já existe e foi associado a '{vendedor.nome_empresa}'.")
            
            if i % 2 == 0:
                vendedor.status_aprovacao = 'aprovado'
                print(f"  Vendedor '{vendedor.nome_empresa}' APROVADO.")
            else:
                vendedor.status_aprovacao = 'pendente'
                print(f"  Vendedor '{vendedor.nome_empresa}' PENDENTE de aprovação.")
            vendedor.save()

        lista_vendedores.append(vendedor)
    
    print(f"Total de {len(lista_vendedores)} vendedores criados.")


    # --- Categorias ---
    print("\nCriando categorias...")
    categorias_nomes = ["Eletrônicos", "Casa e Decoração", "Moda", "Alimentos", "Automotivo",
                        "Saúde e Beleza", "Esportes", "Livros", "Ferramentas", "Jardim",
                        "Viagens", "Serviços", "Cursos", "Pet Shop"]
    categorias = []
    for nome in categorias_nomes:
        categoria, created = Categoria.objects.get_or_create(
            nome=nome,
            defaults={'descricao': fake.text(max_nb_chars=50)}
        )
        categorias.append(categoria)
    print(f"Total de {len(categorias)} categorias criadas.")

    # --- Ofertas (Seu "Produto" Principal) ---
    print("\nCriando 30 ofertas (unidade e lote, ativas, sucessos e falhas)...")
    
    ofertas_data = []

    # 15 Ofertas do tipo 'unidade' (e-commerce normal)
    for i in range(15):
        preco_original = round(random.uniform(50.0, 1500.0), 2)
        preco_desconto = round(preco_original * random.uniform(0.5, 0.9), 2)
        ofertas_data.append({
            'titulo': f"{fake.catch_phrase()} - {fake.random_element(elements=('Premium', 'Ultra', 'Super'))}",
            'vendedor': random.choice([v for v in lista_vendedores if v.status_aprovacao == 'aprovado']),
            'categoria': random.choice(categorias),
            'descricao_detalhada': fake.paragraph(nb_sentences=5),
            'preco_original': preco_original,
            'preco_desconto': preco_desconto,
            'data_inicio': timezone.now() - timedelta(days=random.randint(0, 7)),
            'data_termino': timezone.now() + timedelta(days=random.randint(1, 30)),
            'quantidade_minima_ativacao': 1,
            'quantidade_maxima_cupons': random.randint(50, 500) if random.random() > 0.5 else None,
            'publicada': True,
            'status': 'ativa',
            'destaque': random.random() > 0.7,
            'tipo_oferta': 'unidade',
            'img_url': f"https://picsum.photos/seed/unidade{i}/300/200",
            'quantidade_vendida': 0 # <--- ADICIONADO AQUI
        })

    # 10 Ofertas do tipo 'lote' (compra coletiva)
    for i in range(10):
        preco_original = round(random.uniform(100.0, 2000.0), 2)
        preco_desconto = round(preco_original * random.uniform(0.4, 0.7), 2)
        ofertas_data.append({
            'titulo': f"{fake.bs()} em Lote - {fake.random_element(elements=('Exclusivo', 'Black Friday', 'Mega Desconto'))}",
            'vendedor': random.choice([v for v in lista_vendedores if v.status_aprovacao == 'aprovado']),
            'categoria': random.choice(categorias),
            'descricao_detalhada': fake.paragraph(nb_sentences=6),
            'preco_original': preco_original,
            'preco_desconto': preco_desconto,
            'data_inicio': timezone.now() - timedelta(days=random.randint(0, 3)),
            'data_termino': timezone.now() + timedelta(minutes=random.randint(5, 60)), # Curto para testar o Celery/Cron
            'quantidade_minima_ativacao': random.randint(5, 20),
            'quantidade_maxima_cupons': random.randint(20, 100),
            'publicada': True,
            'status': 'ativa',
            'destaque': random.random() > 0.8,
            'tipo_oferta': 'lote',
            'img_url': f"https://picsum.photos/seed/lote{i}/300/200",
            'quantidade_vendida': 0 # <--- ADICIONADO AQUI
        })

    # 5 Ofertas do tipo 'lote' (já finalizadas no passado - para testar histórico)
    for i in range(5):
        preco_original = round(random.uniform(50.0, 500.0), 2)
        preco_desconto = round(preco_original * random.uniform(0.3, 0.6), 2)
        data_termino_passado = timezone.now() - timedelta(days=random.randint(1, 30))
        
        status_final_lote = random.choice(['sucesso', 'falha_lote'])
        min_ativ = random.randint(5, 15)
        qtd_vendida = min_ativ if status_final_lote == 'sucesso' else random.randint(1, min_ativ - 1)

        ofertas_data.append({
            'titulo': f"{fake.catch_phrase()} (Finalizado)",
            'vendedor': random.choice([v for v in lista_vendedores if v.status_aprovacao == 'aprovado']),
            'categoria': random.choice(categorias),
            'descricao_detalhada': fake.paragraph(nb_sentences=4),
            'preco_original': preco_original,
            'preco_desconto': preco_desconto,
            'data_inicio': data_termino_passado - timedelta(days=random.randint(5, 15)),
            'data_termino': data_termino_passado,
            'quantidade_minima_ativacao': min_ativ,
            'quantidade_maxima_cupons': min_ativ * 2,
            'quantidade_vendida': qtd_vendida,
            'publicada': True,
            'status': status_final_lote,
            'destaque': False,
            'tipo_oferta': 'lote',
            'img_url': f"https://picsum.photos/seed/finalizado{i}/300/200"
        })

    # Cria as ofertas no DB
    lista_ofertas_criadas = []
    for i, oferta_d in enumerate(ofertas_data):
        img_file = None
        if 'img_url' in oferta_d:
            img_file = get_image_from_url(oferta_d['img_url'], f"oferta_{i}.jpg")
        
        oferta, created_oferta = Oferta.objects.get_or_create(
            slug=slugify(oferta_d['titulo']) + f"-{i}", # Garante slug único
            defaults={
                'titulo': oferta_d['titulo'],
                'vendedor': oferta_d['vendedor'],
                'categoria': oferta_d['categoria'],
                'descricao_detalhada': oferta_d['descricao_detalhada'],
                'preco_original': oferta_d['preco_original'],
                'preco_desconto': oferta_d['preco_desconto'],
                'data_inicio': oferta_d['data_inicio'],
                'data_termino': oferta_d['data_termino'],
                'quantidade_minima_ativacao': oferta_d['quantidade_minima_ativacao'],
                'quantidade_maxima_cupons': oferta_d['quantidade_maxima_cupons'],
                'quantidade_vendida': oferta_d['quantidade_vendida'], # <--- AGORA ESTÁ AQUI
                'imagem_principal': img_file,
                'publicada': oferta_d['publicada'],
                'status': oferta_d['status'],
                'destaque': oferta_d['destaque'],
                'tipo_oferta': oferta_d['tipo_oferta']
            }
        )
        if created_oferta:
            print(f"  Oferta '{oferta.titulo}' (Tipo: {oferta.tipo_oferta}) criada.")
        else:
            print(f"  Oferta '{oferta.titulo}' já existe.")
        lista_ofertas_criadas.append(oferta)

    print(f"Total de {len(lista_ofertas_criadas)} ofertas criadas.")

    # --- Simular Compras (para ofertas ativas) e Pedidos Coletivos ---
    print("\nSimulando compras e pedidos coletivos para ofertas ativas...")
    for user_comprador in users_compradores:
        num_compras = random.randint(1, 3) # Cada comprador faz 1 a 3 compras/pedidos
        for _ in range(num_compras):
            oferta_alvo = random.choice([o for o in lista_ofertas_criadas if o.status == 'ativa' and o.publicada])
            
            if oferta_alvo.tipo_oferta == 'unidade':
                with transaction.atomic():
                    compra = Compra.objects.create(
                        usuario=user_comprador,
                        oferta=oferta_alvo,
                        quantidade=1,
                        valor_total=oferta_alvo.preco_desconto,
                        status_pagamento='aprovada', # Simula aprovação
                        id_transacao_mp=fake.uuid4(),
                        metodo_pagamento=random.choice(['cartao_credito', 'pix'])
                    )
                    Cupom.objects.create(
                        compra=compra,
                        oferta=oferta_alvo,
                        usuario=user_comprador,
                        valido_ate=oferta_alvo.data_termino,
                        status='disponivel'
                    )
                    # A quantidade_vendida da oferta JÁ ESTÁ NO CAMPO 'quantidade_vendida' do modelo Oferta
                    # e é atualizada na Tarefa Celery para Lote, ou no Pagamento para Unidade.
                    # Aqui, como já estamos criando, apenas atualizamos a oferta se for uma nova venda.
                    # oferta_alvo.quantidade_vendida += 1 # Não precisa, a notificação MP já fará isso
                    # oferta_alvo.save()
                    print(f"  Compra por unidade #{compra.id} para '{oferta_alvo.titulo}' (comprador: {user_comprador.username})")
            
            elif oferta_alvo.tipo_oferta == 'lote':
                with transaction.atomic():
                    # Para ofertas de lote ativas, o pagamento é aprovado, mas aguarda lote
                    pedido = PedidoColetivo.objects.create(
                        usuario=user_comprador,
                        oferta=oferta_alvo,
                        quantidade=1,
                        valor_unitario=oferta_alvo.preco_desconto,
                        valor_total=oferta_alvo.preco_desconto,
                        status_pagamento='aprovado_mp', # Pagamento aprovado no MP
                        status_lote='aberto', # Lote aguardando concretização
                        id_transacao_mp=fake.uuid4(),
                        metodo_pagamento=random.choice(['cartao_credito', 'boleto'])
                    )
                    # A quantidade_vendida da oferta JÁ ESTÁ NO CAMPO 'quantidade_vendida' do modelo Oferta
                    # e é atualizada na Tarefa Celery para Lote, ou no Pagamento para Unidade.
                    # Aqui, como já estamos criando, apenas atualizamos a oferta se for uma nova venda.
                    # oferta_alvo.quantidade_vendida += 1 # Não precisa, a notificação MP já fará isso
                    # oferta_alvo.save()
                    print(f"  Pedido Coletivo #{pedido.id} para '{oferta_alvo.titulo}' (comprador: {user_comprador.username})")

    # --- Simular Créditos Manuais ou Ajustes ---
    print("\nSimulando algumas transações de crédito (além das automáticas por falha/sucesso de lote)...")
    comprador_com_credito = random.choice(users_compradores)
    credito_obj, created_cred = CreditoUsuario.objects.get_or_create(usuario=comprador_com_credito)
    credito_obj.adicionar_credito(50.00, "Crédito de boas-vindas")
    credito_obj.usar_credito(15.00, "Uso em compra fictícia")
    print(f"  Crédito ajustado para {comprador_com_credito.username}. Saldo: {credito_obj.saldo}")


    # --- Criar Banners de Teste ---
    print("\nCriando 3 banners de teste...")
    from ofertas.models import Banner # Importe Banner aqui
    
    banners_data = [
        {'titulo': 'Grande Liquidação de Verão', 'img_url': 'https://picsum.photos/seed/banner1/1200/400', 'url_destino': reverse('ofertas:lista_ofertas'), 'ordem': 1},
        {'titulo': 'Aproveite Nossos Lotes Exclusivos', 'img_url': 'https://picsum.photos/seed/banner2/1200/400', 'url_destino': reverse('ofertas:compre_junto'), 'ordem': 2},
        {'titulo': 'Novos Parceiros no VarejoUnido!', 'img_url': 'https://picsum.photos/seed/banner3/1200/400', 'url_destino': reverse('ofertas:lista_ofertas'), 'ordem': 3},
    ]

    for i, banner_d in enumerate(banners_data):
        img_file = get_image_from_url(banner_d['img_url'], f"banner_{i}.jpg")
        Banner.objects.get_or_create(
            titulo=banner_d['titulo'],
            defaults={
                'imagem': img_file,
                'url_destino': banner_d['url_destino'],
                'ativo': True,
                'ordem': banner_d['ordem']
            }
        )
        print(f"  Banner '{banner_d['titulo']}' criado.")


    print("\n--- População de dados concluída com sucesso! ---")
    print("Lembre-se de iniciar Celery Worker e Celery Beat (ou configurar Cron Jobs) para que as ofertas de LOTE sejam processadas!")


if __name__ == '__main__':
    clear_db()
    populate_data()