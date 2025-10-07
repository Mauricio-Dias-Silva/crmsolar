import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from uuid import uuid4
# Importa os modelos necessários
from produtos.models import Produto, Pedido, Item, RegiaoFrete
from solar.models import Cliente, Projeto, Fornecedor, Etapa, Financeiro, DocumentoProjeto
from mp_integracao.models import TransacaoMercadoPago


# Cria documentos de exemplo
                    for _ in range(random.randint(1, 3)):
                        # A linha abaixo é a que precisa ser corrigida
                        # nome=f'Doc_{fake.unique.word()}'  <-- ESTA LINHA CAUSA O ERRO

                        # Substitua por esta linha para garantir unicidade
                        DocumentoProjeto.objects.create(
                            projeto=projeto,
                            nome=f'Doc_{fake.word().title()}_{uuid4()}', # <--- CORREÇÃO AQUI
                            arquivo=f'documentos/projeto_{projeto.id}/doc_{uuid4()}.pdf', # OPCIONAL: Ajuste aqui também para garantir nome de arquivo único
                            visivel_cliente=True,
                            data_upload=fake.date_time_between(start_date=projeto.data_inicio, end_date='now')
                        )

User = get_user_model()
fake = Faker('pt_BR')

class Command(BaseCommand):
    help = 'Popula o banco de dados com projetos e pedidos de exemplo.'

    def add_arguments(self, parser):
        parser.add_argument('--max_pedidos_por_cliente', type=int, default=5,
                            help='Número máximo de pedidos por cliente de e-commerce. Default: 5')
        parser.add_argument('--max_projetos_por_cliente', type=int, default=4,
                            help='Número máximo de projetos por cliente de CRM. Default: 4')

    def handle(self, *args, **options):
        self.max_pedidos_por_cliente = options['max_pedidos_por_cliente']
        self.max_projetos_por_cliente = options['max_projetos_por_cliente']

        self.stdout.write(self.style.MIGRATE_HEADING('Iniciando populacao de projetos e pedidos...'))

        with transaction.atomic():
            self.clear_data()
            self.create_data()
        
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Populacao de projetos e pedidos concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*50))

    def clear_data(self):
        self.stdout.write('Limpando dados existentes (Projetos e Pedidos)...')
        try:
            TransacaoMercadoPago.objects.all().delete()
            Item.objects.all().delete()
            Pedido.objects.all().delete()
            DocumentoProjeto.objects.all().delete()
            Financeiro.objects.all().delete()
            Etapa.objects.all().delete()
            Projeto.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Limpeza concluída.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO ao limpar dados: {e}'))
            raise e 

    def create_data(self):
        self.stdout.write(self.style.NOTICE('\n--- Criando Projetos e Pedidos ---'))
        
        clientes_com_perfil = list(Cliente.objects.filter(usuario__isnull=False, nome__isnull=False))
        staff_crm_users = list(User.objects.filter(is_crm_staff=True))
        produtos_ativos = list(Produto.objects.filter(is_active=True, stock__gt=0))
        fornecedores_existentes = list(Fornecedor.objects.all())

        if not clientes_com_perfil or not staff_crm_users or not produtos_ativos or not fornecedores_existentes:
            self.stdout.write(self.style.WARNING('Dados de base (Clientes, Staff, Produtos ou Fornecedores) não encontrados. Pulando criação de Projetos e Pedidos.'))
            return
        
        projeto_status_choices = ['Em andamento', 'Concluído', 'Pendente Orçamento', 'Em Instalação', 'Homologado']
        etapas_padrao = [
            'Levantamento Técnico', 'Elaboração do Projeto', 'Homologação', 'Instalação', 'Comissionamento'
        ]

        for cliente in clientes_com_perfil:
            # Criando projetos para este cliente
            for _ in range(random.randint(1, self.max_projetos_por_cliente)):
                try:
                    projeto_status = random.choice(projeto_status_choices)
                    projeto_data_inicio = fake.date_between(start_date='-1y', end_date='-30d')
                    
                    projeto = Projeto.objects.create(
                        nome=f'Projeto {fake.word().title()} #{random.randint(1000, 9999)} - {cliente.nome}',
                        cliente=cliente,
                        status=projeto_status,
                        data_inicio=projeto_data_inicio,
                        responsavel=random.choice(staff_crm_users),
                        valor_total=Decimal(random.uniform(10000, 50000)).quantize(Decimal('0.01')),
                        fornecedor=random.choice(fornecedores_existentes),
                        potencia_kwp=Decimal(random.uniform(3, 15)).quantize(Decimal('0.01')),
                        quantidade_modulos=random.randint(10, 40),
                        inversor=random.choice(['Inversor A', 'Inversor B', 'Inversor C']),
                        cidade=fake.city(),
                        estado=fake.state_abbr(),
                        rua=fake.street_name(),
                        numero=str(random.randint(1, 2000)),
                        bairro=fake.bairro(),
                        cep=fake.postcode()
                    )
                    
                    # Cria as etapas do projeto
                    num_etapas_concluidas = 0
                    if projeto_status == 'Concluído':
                        num_etapas_concluidas = len(etapas_padrao)
                    elif projeto_status == 'Em andamento' or projeto_status == 'Em Instalação':
                        num_etapas_concluidas = random.randint(1, len(etapas_padrao) - 1)
                    
                    for i, etapa_nome in enumerate(etapas_padrao):
                        data_inicio_etapa = projeto.data_inicio + timedelta(days=i * 5)
                        data_fim_etapa = None
                        if i < num_etapas_concluidas:
                            data_fim_etapa = data_inicio_etapa + timedelta(days=random.randint(3, 10))
                        
                        Etapa.objects.create(
                            projeto=projeto,
                            nome=etapa_nome,
                            status='Concluído' if data_fim_etapa else 'Em Andamento' if i == num_etapas_concluidas else 'Pendente',
                            data_inicio=data_inicio_etapa,
                            data_fim=data_fim_etapa
                        )

                    # Cria lançamentos financeiros para o projeto
                    total_pago = Decimal('0.00')
                    num_lancamentos = random.randint(1, 3)
                    for _ in range(num_lancamentos):
                        valor = Decimal(random.uniform(500, 5000)).quantize(Decimal('0.01'))
                        status_financeiro = 'pago' if random.random() > 0.3 else 'pendente'
                        if status_financeiro == 'pago':
                            total_pago += valor
                        
                        Financeiro.objects.create(
                            projeto=projeto,
                            valor=valor,
                            status=status_financeiro,
                        )
                    
                    # Cria documentos de exemplo
                    for _ in range(random.randint(1, 3)):
                        DocumentoProjeto.objects.create(
                            projeto=projeto,
                            nome=f'Doc_{fake.unique.word()}',
                            arquivo=f'documentos/projeto_{projeto.id}/doc_{fake.unique.word()}.pdf',
                            visivel_cliente=True,
                            data_upload=fake.date_time_between(start_date=projeto.data_inicio, end_date='now')
                        )

                    self.stdout.write(f"  - Projeto '{projeto.nome}' criado para {cliente.nome}.")
                except (IntegrityError, ValidationError) as e:
                    self.stdout.write(self.style.WARNING(f"    - Erro ao criar projeto para {cliente.nome}: {e}. Pulando."))
                    continue
            
            # Criando pedidos para este cliente (mantido como está)
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
                    num_itens = random.randint(1, min(3, len(produtos_ativos)))
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