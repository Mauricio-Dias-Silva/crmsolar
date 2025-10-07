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
def validar_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if not re.compile(r'^\d{14}$').match(cnpj):
        raise ValidationError("CNPJ inválido. O campo CNPJ deve conter exatamente 14 dígitos numéricos.")
    return cnpj

def generate_valid_phone():
    while True:
        phone_number = re.sub(r'\D', '', fake.phone_number())
        if len(phone_number) == 10 or len(phone_number) == 11:
            return phone_number

class Command(BaseCommand):
    help = 'Adiciona clientes Pessoa Jurídica (CNPJ) ao banco de dados sem apagar os dados existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--num_clientes', type=int, default=10,
                            help='Número de clientes PJ a serem criados. Default: 10')

    def handle(self, *args, **kwargs):
        num_clientes = kwargs['num_clientes']
        
        self.stdout.write(self.style.MIGRATE_HEADING(f'Adicionando {num_clientes} clientes Pessoa Jurídica...'))

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
                    user.first_name = fake.company()
                    user.last_name = '' 
                    user.save()
                    
                    doc_identificador = validar_cnpj(fake.unique.cnpj().replace('.', '').replace('/', '').replace('-', ''))
                    
                    Cliente.objects.create(
                        usuario=user,
                        nome=user.first_name,
                        email=user.email,
                        telefone=generate_valid_phone(),
                        rua=fake.street_name(),
                        numero=fake.building_number(),
                        bairro=fake.city_suffix(),
                        cep=fake.postcode().replace('-', ''),
                        cidade=fake.city(),
                        estado=fake.state_abbr(),
                        cnpj=doc_identificador,
                        possui_whatsapp=fake.boolean(chance_of_getting_true=75)
                    )
                    
                    self.stdout.write(f'  - Cliente PJ criado: {user.username}')
                    break
                
                except (ValidationError, IntegrityError) as e:
                    self.stdout.write(self.style.WARNING(f"    - Erro ao criar cliente PJ: {e}. Tentando novamente... (Tentativa {retries + 1}/{max_retries})"))
                    retries += 1
                    try:
                        user.delete()
                    except:
                        pass
                    continue
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    - Erro inesperado ao criar cliente PJ: {e}. Desistindo."))
                    break
            
            if retries == max_retries:
                self.stdout.write(self.style.ERROR(f"    - Falha ao criar cliente PJ após {max_retries} tentativas. Abortando."))

        self.stdout.write(self.style.SUCCESS('\nPopulação de clientes PJ concluída.'))