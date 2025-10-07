import random
import re
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError, OperationalError
from django.contrib.auth.hashers import make_password, check_password

# Importa todos os modelos necessários
from produtos.models import Produto, ProdutoImage, Pedido, Item, RegiaoFrete, CarouselImage 
from solar.models import Usuario, Cliente, Projeto, Etapa, Material, Fornecedor, LancamentoFinanceiro, Departamento, MenuPermissao, DocumentoProjeto
from mp_integracao.models import TransacaoMercadoPago

User = get_user_model()
fake = Faker('pt_BR')

# --- Funções de Validação ---
def validar_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj) 
    if not re.compile(r'^\d{14}$').match(cnpj):
        raise ValidationError("CNPJ inválido. O campo CNPJ deve conter exatamente 14 dígitos numéricos.")
    return cnpj

def validar_telefone(telefone):
    telefone = re.sub(r'[^0-9]', '', telefone) 
    if not re.compile(r'^\d{10,11}$').match(telefone):
        raise ValidationError("Telefone inválido. O campo Telefone deve conter entre 10 e 11 dígitos numéricos.")
    return telefone

def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf) 
    if not re.compile(r'^\d{11}$').match(cpf):
        raise ValidationError("CPF inválido. O campo CPF deve conter exatamente 11 dígitos numéricos.")
    return cpf

def generate_valid_phone():
    while True:
        phone_number = re.sub(r'\D', '', fake.phone_number())
        if len(phone_number) == 10 or len(phone_number) == 11:
            return phone_number

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo completos e realistas, inspirados no catálogo da NeoSolar.'

    def add_arguments(self, parser):
        parser.add_argument('--num_clientes_adicionais', type=int, default=30,
                            help='Número de clientes adicionais a serem criados. Default: 30')
        parser.add_argument('--num_staff_adicionais', type=int, default=8,
                            help='Número de usuários staff adicionais para o CRM. Default: 8')
        parser.add_argument('--num_produtos_adicionais', type=int, default=40,
                            help='Número de produtos adicionais a serem criados no E-commerce (além dos detalhados). Default: 40')
        parser.add_argument('--max_pedidos_por_cliente', type=int, default=5,
                            help='Número máximo de pedidos por cliente de e-commerce. Default: 5')
        parser.add_argument('--max_projetos_por_cliente', type=int, default=4,
                            help='Número máximo de projetos por cliente de CRM. Default: 4')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.departamentos_criados = {}
        self.fornecedores = []
        self.materiais_crm = []

    def handle(self, *args, **kwargs):
        self.num_clientes_adicionais = kwargs['num_clientes_adicionais']
        self.num_staff_adicionais = kwargs['num_staff_adicionais']
        self.num_produtos_adicionais = kwargs['num_produtos_adicionais']
        self.max_pedidos_por_cliente = kwargs['max_pedidos_por_cliente']
        self.max_projetos_por_cliente = kwargs['max_projetos_por_cliente']

        self.stdout.write(self.style.MIGRATE_HEADING('Iniciando populacao do banco de dados com dados realistas...'))

        self.clear_data()
        self.create_data()

        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Populacao do banco de dados concluida com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*50))

    def clear_data(self):
        self.stdout.write('Limpando dados existentes (ordem inversa de dependência)...')
        try:
            TransacaoMercadoPago.objects.all().delete()
            Item.objects.all().delete()
            Pedido.objects.all().delete()
            
            ProdutoImage.objects.all().delete()
            Produto.objects.all().delete()
            
            CarouselImage.objects.all().delete()
            RegiaoFrete.objects.all().delete()

            DocumentoProjeto.objects.all().delete()
            LancamentoFinanceiro.objects.all().delete()
            Etapa.objects.all().delete()
            Projeto.objects.all().delete()
            
            Cliente.objects.all().delete() 
            Usuario.objects.all().delete() 
            Fornecedor.objects.all().delete()
            Material.objects.all().delete()
            
            Departamento.objects.all().delete()
            MenuPermissao.objects.all().delete()
            
            User.objects.filter(is_superuser=False).exclude(username='superadmin_real').delete() 
            self.stdout.write(self.style.SUCCESS('Limpeza concluída.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO ao limpar dados: {e}'))
            raise e 

    def create_data(self):
        self.stdout.write(self.style.NOTICE('\n--- Populando dados de base: Menus, Departamentos e Usuários ---'))
        
        # --- 1. POPULANDO MENUS E DEPARTAMENTOS ---
        menu_items_data = [
            {'nome': 'Dashboard CRM', 'rota': '/crm/'},
            {'nome': 'Clientes CRM', 'rota': '/crm/clientes/'},
            {'nome': 'Projetos CRM', 'rota': '/crm/projetos/'},
            {'nome': 'Materiais CRM', 'rota': '/crm/materiais/'},
            {'nome': 'Financeiro CRM', 'rota': '/crm/financeiro/'},
            {'nome': 'Relatórios CRM', 'rota': '/crm/relatorios/'},
            {'nome': 'Produtos E-commerce (Gestão)', 'rota': '/crm/produtos-ecommerce/'},
            {'nome': 'Usuários (Gestão)', 'rota': '/crm/usuarios/'},
            {'nome': 'Fornecedores CRM', 'rota': '/crm/fornecedores/'},
            {'nome': 'Dashboard Cliente', 'rota': '/crm/cliente/dashboard/'},
            {'nome': 'Meus Pedidos', 'rota': '/crm/cliente/meus-pedidos/'},
        ]
        for item_data in menu_items_data:
            MenuPermissao.objects.get_or_create(nome=item_data['nome'], rota=item_data['rota'])
        self.stdout.write('  - Permissões de Menu criadas.')

        deps_info_list = [
            {'nome': 'Administracao', 'perm_menus': ['Dashboard CRM', 'Clientes CRM', 'Projetos CRM', 'Materiais CRM', 'Financeiro CRM', 'Relatórios CRM', 'Produtos E-commerce (Gestão)', 'Usuários (Gestão)', 'Fornecedores CRM']},
            {'nome': 'Vendas', 'perm_menus': ['Dashboard CRM', 'Clientes CRM', 'Projetos CRM', 'Financeiro CRM']},
            {'nome': 'Instalacao', 'perm_menus': ['Dashboard CRM', 'Projetos CRM', 'Materiais CRM']},
            {'nome': 'Suporte', 'perm_menus': ['Dashboard CRM', 'Clientes CRM', 'Projetos CRM']},
            {'nome': 'Marketing', 'perm_menus': ['Dashboard CRM', 'Produtos E-commerce (Gestão)']},
            {'nome': 'Financeiro', 'perm_menus': ['Dashboard CRM', 'Financeiro CRM', 'Clientes CRM', 'Projetos CRM']},
        ]
        
        self.departamentos_criados = {} 
        for dep_data in deps_info_list:
            dep, created = Departamento.objects.get_or_create(nome=dep_data['nome'])
            self.departamentos_criados[dep_data['nome']] = dep
        self.stdout.write('  - Departamentos criados e mapeados.')

        # --- 2. POPULANDO USUÁRIOS E CLIENTES ---
        self.stdout.write(self.style.NOTICE('\n--- Criando usuários base e clientes de teste ---'))
        
        admin_user = User.objects.create_superuser(
            username='superadmin', 
            email='superadmin@example.com', 
            password='superadminpass'
        )
        admin_user.is_crm_staff = True
        admin_user.first_name = 'Super'
        admin_user.last_name = 'Admin'
        admin_user.save()
        self.stdout.write("  - Superusuário 'superadmin' criado com sucesso!")

        staff_user = User.objects.create_user(
            username='stafftest', 
            email='stafftest@example.com', 
            password='staffpass'
        )
        staff_user.is_crm_staff = True
        staff_user.is_staff = True
        staff_user.departamento = self.departamentos_criados['Vendas']
        staff_user.first_name = 'Staff'
        staff_user.last_name = 'Teste'
        staff_user.save()
        self.stdout.write("  - Usuário Staff 'stafftest' criado com sucesso!")
        perm_menus_for_vendas = next((item['perm_menus'] for item in deps_info_list if item['nome'] == 'Vendas'), [])
        for menu_name in perm_menus_for_vendas:
            try:
                menu_perm = MenuPermissao.objects.get(nome=menu_name)
                staff_user.permissoes_menu.add(menu_perm)
            except MenuPermissao.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"    - Permissão de menu '{menu_name}' não encontrada para 'stafftest'."))

        clientefull_user = User.objects.create_user(
            username='clientefull', 
            email='clientefull@example.com', 
            password='clientepass'
        )
        clientefull_user.is_customer = True
        clientefull_user.first_name = 'Cliente'
        clientefull_user.last_name = 'Completo'
        clientefull_user.save()
        self.stdout.write("  - Usuário Cliente Completo 'clientefull' criado com sucesso!")
        
        try:
            Cliente.objects.create(
                usuario=clientefull_user, nome='Cliente Teste Completo', email='clientefull@example.com',
                telefone=validar_telefone('11987654321'),
                rua='Rua Completa', numero='100', bairro='Centro',
                cep='01000000', cidade='São Paulo', estado='SP', cpf=validar_cpf('11122233344'),
                possui_whatsapp=True
            )
            self.stdout.write("  - Perfil Cliente para 'clientefull' criado.")
        except (ValidationError, IntegrityError) as e:
            self.stdout.write(self.style.ERROR(f"    - Erro ao criar Perfil Cliente para 'clientefull': {e}"))

        clientenoprofile_user = User.objects.create_user(
            username='clientenoprofile', 
            email='clientenoprofile@example.com', 
            password='clientepass'
        )
        clientenoprofile_user.is_customer = True
        clientenoprofile_user.first_name = 'Cliente'
        clientenoprofile_user.last_name = 'Sem Perfil'
        clientenoprofile_user.save()
        self.stdout.write("  - Usuário 'clientenoprofile' (sem perfil) criado com sucesso!")

        self.stdout.write(self.style.SUCCESS('\n--- Usuários e perfis de base criados. ---'))

        # --- 3. POPULANDO DADOS DO E-COMMERCE ---
        self.stdout.write(self.style.NOTICE('\n--- Criando Produtos do E-commerce, Carrossel e Frete ---'))
        
        categorias_str = [
            'paineis_solares', 'inversores', 'baterias', 'kits_fotovoltaicos', 'estruturas_montagem',
            'acessorios', 'ferramentas_instalacao', 'sistemas_backup', 'outros_componentes', 'monitoramento'
        ]
        
        carousel_data = [
            {'title': 'Energia Solar ao Seu Alcance', 'description': 'Economia e sustentabilidade para sua casa ou negócio. Simule já!', 'image': 'carousel/banner_economia.png'},
            {'title': 'As Melhores Marcas do Mundo', 'description': 'Trabalhamos com os líderes globais em painéis e inversores.', 'image': 'carousel/banner_marcas.png'},
        ]
        for i, data in enumerate(carousel_data):
            CarouselImage.objects.get_or_create(title=data['title'], defaults={'description': data['description'], 'image': data['image'], 'is_active': (i == 0)})
        self.stdout.write('  - Imagens de carrossel criadas.')

        regioes_frete_data = [
            {'prefixo_cep': '010', 'cidade': 'São Paulo', 'valor_frete': 50.00, 'prazo_entrega': 3}, 
            {'prefixo_cep': '060', 'cidade': 'Osasco', 'valor_frete': 30.00, 'prazo_entrega': 2},
            {'prefixo_cep': '200', 'cidade': 'Rio de Janeiro', 'valor_frete': 120.00, 'prazo_entrega': 5},
        ]
        for reg_data in regioes_frete_data:
            RegiaoFrete.objects.get_or_create(prefixo_cep=reg_data['prefixo_cep'], defaults={'cidade': reg_data['cidade'], 'valor_frete': Decimal(str(reg_data['valor_frete'])).quantize(Decimal('0.01')), 'prazo_entrega': reg_data['prazo_entrega']})
        self.stdout.write('  - Regiões de frete criadas.')

        produtos_ecommerce_detalhes = [
            {"name": "Painel Solar Jinko Tiger Pro 550W Half-Cell", "description": "Módulo de alta eficiência...", "preco": 820.00, "categoria_slug": "paineis_solares", "sku": "JKM550M-72HL4", "peso": 28.0, "garantia": "12 anos", "images": ["produtos/jinko_tiger_pro_550w_main.png"]},
            {"name": "Inversor Growatt SPH 10000TL3-BH (Híbrido)", "description": "Inversor trifásico híbrido...", "preco": 10500.00, "categoria_slug": "inversores", "sku": "GRW-SPH10000TL3", "peso": 28.0, "garantia": "10 anos", "images": ["produtos/growatt_sph10000_main.png"], "stock": 25},
        ]
        
        for prod_data in produtos_ecommerce_detalhes:
            try:
                produto, created = Produto.objects.get_or_create(sku=prod_data['sku'], defaults={'name': prod_data['name'], 'description': prod_data['description'], 'preco': Decimal(str(prod_data['preco'])).quantize(Decimal('0.01')), 'categoria_id': prod_data['categoria_slug'], 'stock': prod_data.get('stock', 10), 'is_active': True, 'peso': Decimal(str(prod_data.get('peso'))).quantize(Decimal('0.01')) if prod_data.get('peso') else None, 'garantia': prod_data.get('garantia')})
                if created:
                    for i, image_path in enumerate(prod_data['images']):
                        ProdutoImage.objects.create(produto=produto, image=image_path, alt_text=f'Imagem de {produto.name}', is_main=(i == 0))
                    self.stdout.write(f'  - Produto E-commerce criado: {produto.name} (SKU: {produto.sku})')
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Erro de integridade ao criar Produto {prod_data.get('name', 'N/A')}: {e}"))
        self.stdout.write(self.style.SUCCESS('\n--- Populacao de produtos e dados de e-commerce concluida. ---'))

        # --- 4. POPULANDO DADOS DO CRM (FORNECEDORES, MATERIAIS) ---
        self.stdout.write(self.style.NOTICE('\n--- Criando Fornecedores e Materiais de estoque ---'))

        fornecedores_data = [{'nome': 'Canadian Solar Inc.', 'cnpj': '07.319.467/0001-44', 'telefone': '1130301000', 'email': 'contato@canadiansolar.com.br', 'endereco': 'Av. Eng. Luís Carlos Berrini, 105 - São Paulo - SP'}, {'nome': 'JinkoSolar Holding Co., Ltd.', 'cnpj': '07.319.467/0002-25', 'telefone': '1130301001', 'email': 'info@jinkosolar.com', 'endereco': 'Rua Tabapuã, 140 - São Paulo - SP'}]
        for data in fornecedores_data:
            try:
                Fornecedor.objects.get_or_create(nome=data['nome'], defaults={'cnpj': validar_cnpj(data['cnpj']), 'telefone': validar_telefone(data['telefone']), 'email': data['email'], 'endereco': data['endereco']})
            except (ValidationError, IntegrityError) as e:
                self.stdout.write(self.style.ERROR(f"Erro ao criar Fornecedor {data['nome']}: {e}"))
        self.stdout.write('  - Fornecedores criados.')
        self.fornecedores = list(Fornecedor.objects.all())

        material_details = [{"name": "Painel Solar JA Solar 550W", "manufacturer": "JA Solar", "model": "JAM72S30-550/GR", "unit": "un", "buy_price": 720.00, "sell_price": 890.00, "warranty_months": 144, "weight": 27.8, "notes": "Módulo de alta potência..."}]
        for mat_data in material_details:
            data_entrada_material = fake.date_between(start_date='-2y', end_date='today')
            garantia_data = data_entrada_material + timedelta(days=mat_data['warranty_months'] * 30) if mat_data.get('warranty_months') is not None else None
            try:
                Material.objects.get_or_create(nome=mat_data['name'], defaults={'codigo': fake.unique.ean8(), 'fabricante': mat_data['manufacturer'], 'modelo': mat_data.get('model'), 'unidade_medida': mat_data['unit'], 'quantidade_estoque': random.randint(5, 200), 'estoque_minimo': random.randint(1, 10), 'localizacao': random.choice(['Armazém Principal']), 'preco_compra': Decimal(str(mat_data['buy_price'])).quantize(Decimal('0.01')), 'preco_venda': Decimal(str(mat_data.get('sell_price'))).quantize(Decimal('0.01')), 'garantia_ate': garantia_data, 'data_entrada': data_entrada_material, 'observacoes': mat_data.get('notes')})
            except (ValidationError, IntegrityError) as e:
                self.stdout.write(self.style.ERROR(f"Erro ao criar Material {mat_data['name']}: {e}"))
        self.stdout.write('  - Materiais criados.')

        self.stdout.write(self.style.SUCCESS('\n--- Populacao de fornecedores e materiais concluida. ---'))

        # --- 5. POPULANDO PROJETOS E PEDIDOS (DEPOIS DA BASE) ---
        self.stdout.write(self.style.NOTICE('\n--- Criando Projetos, Etapas, Lançamentos e Pedidos ---'))
        clientes_com_perfil = list(Cliente.objects.filter(usuario__isnull=False, nome__isnull=False))
        staff_crm_users = list(User.objects.filter(is_crm_staff=True))
        produtos_ativos = list(Produto.objects.filter(is_active=True, stock__gt=0))

        if not clientes_com_perfil or not staff_crm_users or not produtos_ativos:
            self.stdout.write(self.style.WARNING('Nenhum Cliente com perfil ou Staff encontrado. Pulando criação de Projetos e Pedidos.'))
            return
        
        for cliente in clientes_com_perfil:
            # Criando projetos para este cliente
            for _ in range(random.randint(1, self.max_projetos_por_cliente)):
                try:
                    projeto_status = random.choice(['Em andamento', 'Concluído', 'Pendente Orçamento'])
                    projeto_data_inicio = fake.date_between(start_date='-2y', end_date='-30d')
                    projeto = Projeto.objects.create(
                        nome=f'Projeto {fake.unique.word().title()} para {cliente.nome}',
                        cliente=cliente,
                        status=projeto_status,
                        data_inicio=projeto_data_inicio,
                        responsavel=random.choice(staff_crm_users),
                        valor_total=Decimal(random.uniform(10000, 50000)).quantize(Decimal('0.01')),
                        fornecedor=random.choice(fornecedores_existentes)
                    )
                    self.stdout.write(f"  - Projeto '{projeto.nome}' criado para {cliente.nome}.")
                except (IntegrityError, ValidationError) as e:
                    self.stdout.write(self.style.WARNING(f"    - Erro ao criar projeto para {cliente.nome}: {e}. Pulando."))
                    continue
            
            # Criando pedidos para este cliente
            for _ in range(random.randint(1, self.max_pedidos_por_cliente)):
                try:
                    metodo_pag = random.choice(['stripe', 'mercadopago'])
                    status_pedido = random.choice(['pago', 'pendente', 'cancelado', 'enviado'])
                    data_criacao = fake.date_time_between(start_date='-1y', end_date='now')

                    pedido = Pedido.objects.create(
                        usuario=cliente.usuario,
                        email_cliente=cliente.email,
                        total=Decimal('0.00'),
                        status=status_pedido,
                        metodo_pagamento=metodo_pag,
                        criado_em=data_criacao,
                        data_pagamento=data_criacao if status_pedido == 'pago' else None,
                    )
                    
                    total_pedido = Decimal('0.00')
                    num_itens = random.randint(1, min(3, len(produtos_ativos))) # CORRIGIDO AQUI
                    itens_selecionados = random.sample(produtos_ativos, num_itens)
                    for prod in itens_selecionados:
                        qtd = random.randint(1, 5)
                        subtotal = prod.preco * Decimal(qtd)
                        Item.objects.create(pedido=pedido, produto_id_original=prod.id, nome=prod.name, preco_unitario=prod.preco, quantidade=qtd, subtotal=subtotal)
                        total_pedido += subtotal
                    
                    if total_pedido > 0:
                        cep_prefixo = cliente.cep[:3] if cliente.cep else '000'
                        regiao_frete = RegiaoFrete.objects.filter(prefixo_cep=cep_prefixo).first()
                        valor_frete = regiao_frete.valor_frete if regiao_frete else Decimal('50.00')
                        pedido.total = total_pedido + valor_frete
                        pedido.save()
                        self.stdout.write(f"  - Pedido {pedido.id} criado para {cliente.nome}.")
                except (IntegrityError, ValidationError) as e:
                    self.stdout.write(self.style.WARNING(f"    - Erro ao criar pedido para {cliente.nome}: {e}. Pulando."))
                    continue

        self.stdout.write(self.style.SUCCESS('\n--- Populacao de projetos e pedidos concluida. ---'))