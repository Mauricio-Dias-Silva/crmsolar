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

# Importa os modelos necessários para este script
from solar.models import Usuario, Cliente, Departamento, MenuPermissao

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
    help = 'Popula o banco de dados com usuários de exemplo, incluindo staff, clientes e departamentos.'

    def add_arguments(self, parser):
        parser.add_argument('--num_clientes_adicionais', type=int, default=30,
                            help='Número de clientes adicionais a serem criados. Default: 30')
        parser.add_argument('--num_staff_adicionais', type=int, default=8,
                            help='Número de usuários staff adicionais para o CRM. Default: 8')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.departamentos_criados = {}

    def handle(self, *args, **kwargs):
        self.num_clientes_adicionais = kwargs['num_clientes_adicionais']
        self.num_staff_adicionais = kwargs['num_staff_adicionais']

        self.stdout.write(self.style.MIGRATE_HEADING('Iniciando populacao de usuários e clientes...'))

        self.clear_data()
        self.create_data()

        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Populacao de usuários concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*50))

    def clear_data(self):
        self.stdout.write('Limpando dados de usuários e clientes existentes...')
        try:
            Cliente.objects.all().delete()
        except OperationalError as e:
            self.stdout.write(self.style.WARNING(f'Aviso durante a limpeza de Cliente: {e}. Ignorando.'))
            pass
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO ao limpar dados de Cliente: {e}'))
            raise e

        try:
            Usuario.objects.all().delete()
            Departamento.objects.all().delete()
            MenuPermissao.objects.all().delete()
            User.objects.filter(is_superuser=False).exclude(username='superadmin_real').delete()
            self.stdout.write(self.style.SUCCESS('Limpeza concluída.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO ao limpar dados: {e}'))
            raise e

    def create_data(self):
        self.stdout.write(self.style.NOTICE('\n--- Criando usuários, departamentos e permissões de menu ---'))

        # Permissões de Menu
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

        # Departamentos e suas permissões
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

        # Usuários Base - Superadmin e Staff de Teste
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
        
        if not hasattr(clientefull_user, 'perfil_cliente'):
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

        # --- A criação de usuários adicionais e clientes adicionais foi removida daqui. ---
        # A lógica para isso agora estará nos scripts separados que vamos criar.