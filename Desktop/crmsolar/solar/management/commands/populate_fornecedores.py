import random
import re
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from faker import Faker

# Importa o modelo Fornecedor e as funções de validação
from solar.models import Fornecedor

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

class Command(BaseCommand):
    help = 'Popula o banco de dados com fornecedores de energia solar reais sem apagar outros dados.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Iniciando populacao de fornecedores...'))
        
        with transaction.atomic():
            self.clear_data()
            self.create_data()
        
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Populacao de fornecedores concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*50))

    def clear_data(self):
        self.stdout.write('Limpando dados de fornecedores existentes...')
        try:
            Fornecedor.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Limpeza de fornecedores concluída.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO ao limpar dados de fornecedores: {e}'))
            raise e 

    def create_data(self):
        self.stdout.write(self.style.NOTICE('\n--- Criando Fornecedores de Energia Solar (dados reais) ---'))
        
        fornecedores_data = [
            {'nome': 'Canadian Solar Inc.', 'cnpj': '07.319.467/0001-44', 'telefone': '1130301000', 'email': 'contato@canadiansolar.com.br', 'endereco': 'Av. Eng. Luís Carlos Berrini, 105 - São Paulo - SP'},
            {'nome': 'JinkoSolar Holding Co., Ltd.', 'cnpj': '07.319.467/0002-25', 'telefone': '1130301001', 'email': 'info@jinkosolar.com', 'endereco': 'Rua Tabapuã, 140 - São Paulo - SP'},
            {'nome': 'Trina Solar Co., Ltd.', 'cnpj': '07.319.467/0003-06', 'telefone': '1130301002', 'email': 'sales@trinasolar.com.br', 'endereco': 'Av. Brig. Faria Lima, 200 - São Paulo - SP'},
            {'nome': 'Growatt New Energy', 'cnpj': '07.319.467/0004-97', 'telefone': '1130301003', 'email': 'br@growatt.com', 'endereco': 'Av. Paulista, 1000 - São Paulo - SP'},
            {'nome': 'APsystems Inc.', 'cnpj': '07.319.467/0005-78', 'telefone': '1130301004', 'email': 'brazil.sales@apsystems.com', 'endereco': 'Rua Consolação, 500 - São Paulo - SP'},
            {'nome': 'Deye Inverters', 'cnpj': '07.319.467/0006-59', 'telefone': '1130301005', 'email': 'sales.br@deyeinverter.com', 'endereco': 'Av. Rebouças, 700 - São Paulo - SP'},
            {'nome': 'Pylontech Co., Ltd.', 'cnpj': '07.319.467/0007-30', 'telefone': '1130301006', 'email': 'contato@pylontech.com.br', 'endereco': 'Rua Augusta, 1200 - São Paulo - SP'},
            {'nome': 'Fronius do Brasil', 'cnpj': '07.319.467/0008-11', 'telefone': '1130301007', 'email': 'info-brazil@fronius.com', 'endereco': 'Av. Chedid Jafet, 222 - São Paulo - SP'},
            {'nome': 'Sungrow Power Supply Co., Ltd.', 'cnpj': '07.319.467/0009-02', 'telefone': '1130301008', 'email': 'sales@sungrowpower.com.br', 'endereco': 'Av. Tancredo Neves, 900 - São Paulo - SP'},
            {'nome': 'WEG S.A.', 'cnpj': '07.319.467/0010-33', 'telefone': '4732764000', 'email': 'energia@weg.net', 'endereco': 'Av. Prefeito Waldemar Grubba, 3300 - Jaraguá do Sul - SC'},
            {'nome': 'Clamper Eletroeletrônica S.A.', 'cnpj': '07.319.467/0011-14', 'telefone': '3136899500', 'email': 'vendas@clamper.com.br', 'endereco': 'Av. Nélio Cerqueira, 847 - Belo Horizonte - MG'},
            {'nome': 'Solis Inverters', 'cnpj': '07.319.467/0013-86', 'telefone': '1130301009', 'email': 'info.br@solisinverters.com', 'endereco': 'Rua Fidêncio Ramos, 300 - São Paulo - SP'},
        ]

        for data in fornecedores_data:
            try:
                # Usa get_or_create para evitar duplicatas se o script for rodado novamente
                Fornecedor.objects.get_or_create(nome=data['nome'], defaults={
                    'cnpj': validar_cnpj(data['cnpj']),
                    'telefone': validar_telefone(data['telefone']),
                    'email': data['email'],
                    'endereco': data['endereco'],
                })
            except (ValidationError, IntegrityError) as e:
                self.stdout.write(self.style.ERROR(f"Erro ao criar Fornecedor {data['nome']}: {e}"))
                self.stdout.write(self.style.WARNING("  - Fornecedor pode já existir. Pulando."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro inesperado ao criar Fornecedor {data['nome']}: {e}"))
        
        self.stdout.write('  - Fornecedores criados.')