import random
import re
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from faker import Faker
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth.hashers import make_password

# Importa os modelos necessários
from solar.models import Usuario, Cliente

User = get_user_model()
fake = Faker('pt_BR')

# --- Funções de Validação ---
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
    help = 'Adiciona clientes Pessoa Física (CPF) ao banco de dados sem apagar os dados existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--num_clientes', type=int, default=10,
                            help='Número de clientes CPF a serem criados. Default: 10')

    def handle(self, *args, **kwargs):
        num_clientes = kwargs['num_clientes']
        
        self.stdout.write(self.style.MIGRATE_HEADING(f'Adicionando {num_clientes} clientes Pessoa Física...'))

        for i in range(num_clientes):
            max_retries = 5
            retries = 0
            while retries < max_retries:
                try:
                    fake.unique.clear()
                    username = fake.unique.user_name()
                    email = fake.unique.email()
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='pass123',
                    )
                    user.is_customer = True
                    user.first_name = fake.first_name()
                    user.last_name = fake.last_name()
                    user.save()
                    
                    doc_identificador = validar_cpf(fake.unique.cpf().replace('.', '').replace('-', ''))
                    
                    Cliente.objects.create(
                        usuario=user,
                        nome=fake.name(),
                        email=user.email,
                        telefone=generate_valid_phone(),
                        rua=fake.street_name(),
                        numero=fake.building_number(),
                        bairro=fake.city_suffix(),
                        cep=fake.postcode().replace('-', ''),
                        cidade=fake.city(),
                        estado=fake.state_abbr(),
                        cpf=doc_identificador,
                        possui_whatsapp=fake.boolean(chance_of_getting_true=75)
                    )
                    
                    self.stdout.write(f'  - Cliente PF criado: {user.username}')
                    break
                
                except (ValidationError, IntegrityError) as e:
                    self.stdout.write(self.style.WARNING(f"    - Erro ao criar cliente PF: {e}. Tentando novamente... (Tentativa {retries + 1}/{max_retries})"))
                    retries += 1
                    try:
                        user.delete()
                    except:
                        pass
                    continue
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    - Erro inesperado ao criar cliente PF: {e}. Desistindo."))
                    break
            
            if retries == max_retries:
                self.stdout.write(self.style.ERROR(f"    - Falha ao criar cliente PF após {max_retries} tentativas. Abortando."))

        self.stdout.write(self.style.SUCCESS('\nPopulação de clientes PF concluída.'))
