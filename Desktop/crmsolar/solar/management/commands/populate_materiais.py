import random
import re
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Importa os modelos necessários
from solar.models import Material, Fornecedor

fake = Faker('pt_BR')

class Command(BaseCommand):
    help = 'Popula o banco de dados com materiais de estoque de energia solar.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Iniciando populacao de materiais de estoque...'))
        
        with transaction.atomic():
            self.clear_data()
            self.create_data()
        
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Populacao de materiais concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*50))

    def clear_data(self):
        self.stdout.write('Limpando dados de materiais existentes...')
        try:
            Material.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Limpeza de materiais concluída.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO ao limpar dados de materiais: {e}'))
            raise e 

    def create_data(self):
        self.stdout.write(self.style.NOTICE('\n--- Criando Materiais de Estoque ---'))
        
        fornecedores_existentes = list(Fornecedor.objects.all())

        if not fornecedores_existentes:
            self.stdout.write(self.style.ERROR('Nenhum fornecedor encontrado no banco de dados. Por favor, rode o script `populate_fornecedores` primeiro.'))
            return

        materiais_data = [
            # Paineis Solares
            {"name": "Painel Solar Jinko Tiger Pro 550W", "manufacturer": "JinkoSolar", "model": "JKM550M-72HL4", "unit": "un", "buy_price": 820.00, "sell_price": 950.00, "warranty_months": 144, "notes": "Painel fotovoltaico monocristalino.", "peso": 27.5, "fornecedores_possiveis": ["JinkoSolar Holding Co., Ltd."]},
            {"name": "Painel Solar Trina Vertex 600W", "manufacturer": "Trina Solar", "model": "TSM-DE20", "unit": "un", "buy_price": 900.00, "sell_price": 1050.00, "warranty_months": 144, "notes": "Painel de alta potência para grandes projetos.", "peso": 30.0, "fornecedores_possiveis": ["Trina Solar Co., Ltd."]},
            
            # Inversores
            {"name": "Inversor Growatt SPH 10kW Híbrido", "manufacturer": "Growatt", "model": "SPH 10000TL3 BH", "unit": "un", "buy_price": 10500.00, "sell_price": 12000.00, "warranty_months": 120, "notes": "Inversor híbrido, ideal para sistemas com baterias.", "peso": 28.0, "fornecedores_possiveis": ["Growatt New Energy"]},
            {"name": "Microinversor APsystems DS3", "manufacturer": "APsystems", "model": "DS3", "unit": "un", "buy_price": 2800.00, "sell_price": 3200.00, "warranty_months": 240, "notes": "Microinversor para 2 painéis.", "peso": 4.5, "fornecedores_possiveis": ["APsystems Inc."]},
            {"name": "Inversor Fronius Symo 15.0-3-M", "manufacturer": "Fronius", "model": "SYMO 15.0", "unit": "un", "buy_price": 18000.00, "sell_price": 21000.00, "warranty_months": 120, "notes": "Inversor trifásico para sistemas comerciais.", "peso": 25.0, "fornecedores_possiveis": ["Fronius do Brasil"]},

            # Baterias
            {"name": "Bateria Pylontech US3000C", "manufacturer": "Pylontech", "model": "US3000C", "unit": "un", "buy_price": 7500.00, "sell_price": 8800.00, "warranty_months": 120, "notes": "Bateria de lítio para sistemas de armazenamento.", "peso": 32.0, "fornecedores_possiveis": ["Pylontech Co., Ltd."]},
            
            # Estruturas e Cabos
            {"name": "Estrutura para telhado cerâmico", "manufacturer": "Soprano", "model": "SR-TelhaC", "unit": "un", "buy_price": 35.00, "sell_price": 45.00, "warranty_months": 60, "notes": "Conjunto de fixação para 1 painel.", "peso": 2.0, "fornecedores_possiveis": ["WEG S.A."]},
            {"name": "Cabo solar 6mm² (preto)", "manufacturer": "Prysmian", "model": "Prysolar", "unit": "m", "buy_price": 8.50, "sell_price": 12.00, "warranty_months": 24, "notes": "Cabo fotovoltaico isolado.", "peso": 0.08, "fornecedores_possiveis": ["WEG S.A."]},
        ]

        for data in materiais_data:
            data_entrada_material = fake.date_between(start_date='-2y', end_date='today')
            garantia_data = data_entrada_material + timedelta(days=data['warranty_months'] * 30) if data.get('warranty_months') is not None else None
            
            # Encontrar um fornecedor compatível
            fornecedor_selecionado = random.choice([f for f in fornecedores_existentes if f.nome in data['fornecedores_possiveis']]) if 'fornecedores_possiveis' in data else random.choice(fornecedores_existentes)
            
            try:
                Material.objects.get_or_create(
                    nome=data['name'],
                    modelo=data['model'],
                    defaults={
                        'codigo': fake.unique.ean8(),
                        'fabricante': data['manufacturer'],
                        'unidade_medida': data['unit'],
                        'quantidade_estoque': random.randint(5, 200),
                        'estoque_minimo': random.randint(1, 10),
                        'localizacao': random.choice(['Armazém Principal', 'Armazém Secundário']),
                        'preco_compra': Decimal(str(data['buy_price'])).quantize(Decimal('0.01')),
                        'preco_venda': Decimal(str(data.get('sell_price'))).quantize(Decimal('0.01')),
                        'fornecedor': fornecedor_selecionado,
                        'garantia_ate': garantia_data,
                        'data_entrada': data_entrada_material,
                        'observacoes': data.get('notes'),
                        'peso': Decimal(str(data.get('peso'))).quantize(Decimal('0.01')) if data.get('peso') else None,
                    }
                )
            except (ValidationError, IntegrityError) as e:
                self.stdout.write(self.style.ERROR(f"Erro ao criar Material {data['name']}: {e}"))
                self.stdout.write(self.style.WARNING("  - Material pode já existir. Pulando."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro inesperado ao criar Material {data['name']}: {e}"))
        
        self.stdout.write('  - Materiais criados.')