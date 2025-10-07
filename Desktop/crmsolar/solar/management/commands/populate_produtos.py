import random
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
import os

# Importa os modelos necessários
from produtos.models import Produto, ProdutoImage, RegiaoFrete, CarouselImage

fake = Faker('pt_BR')

class Command(BaseCommand):
    help = 'Popula o banco de dados com produtos do e-commerce, carrossel e regiões de frete.'

    def add_arguments(self, parser):
        parser.add_argument('--num_produtos_adicionais', type=int, default=15,
                            help='Número de produtos genéricos a serem adicionados. Default: 15')
        
    def handle(self, *args, **kwargs):
        self.num_produtos_adicionais = kwargs['num_produtos_adicionais']
        
        self.stdout.write(self.style.MIGRATE_HEADING('Iniciando populacao de dados de e-commerce...'))
        
        with transaction.atomic():
            self.clear_data()
            self.create_data()
        
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Populacao de produtos concluida com sucesso!'))
        self.stdout.write(self.style.SUCCESS('='*50))

    def clear_data(self):
        self.stdout.write('Limpando dados de produtos existentes...')
        try:
            ProdutoImage.objects.all().delete()
            Produto.objects.all().delete()
            CarouselImage.objects.all().delete()
            RegiaoFrete.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Limpeza concluída.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO ao limpar dados: {e}'))
            raise e 

    def create_data(self):
        self.stdout.write(self.style.NOTICE('\n--- Criando dados para o E-commerce (Produtos, Carrossel, Frete) ---'))
        
        categorias_str = [
            'paineis_solares', 'inversores', 'baterias', 
            'kits_fotovoltaicos', 'estruturas_montagem',
            'acessorios', 'ferramentas_instalacao', 'sistemas_backup', 'outros_componentes', 'monitoramento'
        ]
        self.stdout.write('  - Categorias de produtos (strings) definidas para uso.')

        # Carousel Images
        carousel_data = [
            {'title': 'Energia Solar ao Seu Alcance', 'description': 'Economia e sustentabilidade para sua casa ou negócio. Simule já!', 'image': 'carousel/banner_economia.png'},
            {'title': 'As Melhores Marcas do Mundo', 'description': 'Trabalhamos com os líderes globais em painéis e inversores.', 'image': 'carousel/banner_marcas.png'},
            {'title': 'Financiamento Facilitado', 'description': 'Condições especiais para você gerar sua própria energia.', 'image': 'carousel/banner_financiamento.png'},
            {'title': 'Suporte e Instalação Garantidos', 'description': 'Nossa equipe especializada cuida de tudo para você, do projeto à homologação.', 'image': 'carousel/banner_suporte.png'},
        ]
        for i, data in enumerate(carousel_data):
            CarouselImage.objects.get_or_create(title=data['title'], defaults={'description': data['description'], 'image': data['image'], 'is_active': (i == 0)})
        self.stdout.write('  - Imagens de carrossel criadas.')

        # Regiões de Frete
        regioes_frete_data = [
            {'prefixo_cep': '010', 'cidade': 'São Paulo', 'valor_frete': 50.00, 'prazo_entrega': 3}, 
            {'prefixo_cep': '060', 'cidade': 'Osasco', 'valor_frete': 30.00, 'prazo_entrega': 2},
            {'prefixo_cep': '130', 'cidade': 'Campinas', 'valor_frete': 80.00, 'prazo_entrega': 4},
            {'prefixo_cep': '200', 'cidade': 'Rio de Janeiro', 'valor_frete': 120.00, 'prazo_entrega': 5},
            {'prefixo_cep': '300', 'cidade': 'Belo Horizonte', 'valor_frete': 110.00, 'prazo_entrega': 5},
            {'prefixo_cep': '400', 'cidade': 'Salvador', 'valor_frete': 180.00, 'prazo_entrega': 8},
            {'prefixo_cep': '500', 'cidade': 'Recife', 'valor_frete': 200.00, 'prazo_entrega': 9},
            {'prefixo_cep': '600', 'cidade': 'Fortaleza', 'valor_frete': 220.00, 'prazo_entrega': 10},
        ]
        for reg_data in regioes_frete_data:
            RegiaoFrete.objects.get_or_create(prefixo_cep=reg_data['prefixo_cep'], defaults={'cidade': reg_data['cidade'], 'valor_frete': Decimal(str(reg_data['valor_frete'])).quantize(Decimal('0.01')), 'prazo_entrega': reg_data['prazo_entrega']})
        self.stdout.write('  - Regiões de frete criadas.')

        # Produtos do E-commerce (realistas, inspirados na NeoSolar)
        produtos_ecommerce_detalhes = [
            # Paineis Solares
            {"name": "Painel Solar Jinko Tiger Pro 550W Half-Cell", "description": "Módulo de alta eficiência com tecnologia Tiling Ribbon...", "preco": 820.00, "categoria_slug": "paineis_solares", "sku": "JKM550M-72HL4", "peso": 28.0, "dimensoes": "2274x1134x30mm", "garantia": "12 anos", "images": ["produtos/jinko_tiger_pro_550w_main.png"]},
            {"name": "Painel Solar Trina Vertex S 415W", "description": "Design compacto e esteticamente agradável, perfeito para telhados residenciais.", "preco": 680.00, "categoria_slug": "paineis_solares", "sku": "TSM-415DE09R.05", "peso": 21.0, "dimensoes": "1762x1134x30mm", "garantia": "15 anos", "images": ["produtos/trina_vertex_s_415w_main.png"]},
            {"name": "Painel Solar Canadian Solar HiKu7 665W", "description": "Painel fotovoltaico de nova geração, excelente para otimização de espaço e custo.", "preco": 950.00, "categoria_slug": "paineis_solares", "sku": "CS7L-665M", "peso": 34.0, "dimensoes": "2384x1303x35mm", "garantia": "12 anos", "images": ["produtos/canadian_hiku7_665w_main.png"]},
            
            # Inversores On-Grid
            {"name": "Inversor Growatt SPH 10kW Híbrido", "description": "Inversor trifásico híbrido com 2 MPPTs, compatível com baterias...", "preco": 10500.00, "categoria_slug": "inversores", "sku": "GRW-SPH10000TL3", "peso": 28.0, "dimensoes": "505x453x198mm", "garantia": "10 anos", "images": ["produtos/growatt_sph10000_main.png"], "stock": 25},
            {"name": "Inversor Fronius Primo 8.2-1 Light", "description": "Inversor monofásico leve e versátil, com design inovador.", "preco": 7900.00, "categoria_slug": "inversores", "sku": "FRO-PRI82-1L", "peso": 21.5, "dimensoes": "645x431x204mm", "garantia": "7 anos", "images": ["produtos/fronius_primo_8_2_main.png"]},
            {"name": "Inversor SolarEdge SE10K-RWS (Residencial)", "description": "Inversor monofásico otimizado para sistemas residenciais com otimizadores de potência SolarEdge.", "preco": 9800.00, "categoria_slug": "inversores", "sku": "SEDG-SE10K-RWS", "peso": 12.0, "dimensoes": "540x315x191mm", "garantia": "12 anos", "images": ["produtos/solaredge_se10k_main.png"]},
            
            # Microinversores
            {"name": "Microinversor APsystems DS3-S (1500W)", "description": "Microinversor bifásico para até 2 painéis de alta potência, ideal para residências.", "preco": 2400.00, "categoria_slug": "inversores", "sku": "APS-DS3-S", "peso": 3.7, "dimensoes": "262x217x45mm", "garantia": "15 anos", "images": ["produtos/apsystems_ds3s_main.png"]},
            {"name": "Microinversor Hoymiles HMS-2000-4T", "description": "Microinversor trifásico para até 4 painéis, alta performance em instalações comerciais pequenas.", "preco": 3800.00, "categoria_slug": "inversores", "sku": "HM-2000-4T", "peso": 5.0, "dimensoes": "331x218x36mm", "garantia": "12 anos", "images": ["produtos/hoymiles_hms2000_main.png"]},
            
            # Baterias e Armazenamento
            {"name": "Bateria Pylontech US3000C (3.5kWh)", "description": "Módulo de bateria de lítio de baixa tensão para sistemas off-grid e híbridos.", "preco": 7500.00, "categoria_slug": "baterias", "sku": "PYL-US3000C", "peso": 32.0, "dimensoes": "442x420x132mm", "garantia": "7 anos", "images": ["produtos/pylontech_us3000c_main.png", "produtos/pylontech_us3000c_alt1.png"], "stock": 18},
            {"name": "Bateria BYD Battery-Box Premium HVS 5.1 (5.1kWh)", "description": "Solução de bateria de alta tensão da BYD, escalável e segura.", "preco": 12800.00, "categoria_slug": "baterias", "sku": "BYD-HVS5.1", "peso": 65.0, "dimensoes": "713x298x168mm", "garantia": "10 anos", "images": ["produtos/byd_hvs5_1_main.png"]},
            
            # Kits Fotovoltaicos
            {"name": "Kit Solar On-Grid 5.5 kWp Residencial (Jinko/Growatt)", "description": "Sistema completo para residências com consumo médio/alto. Inclui painéis Jinko e inversor Growatt.", "preco": 28000.00, "categoria_slug": "kits_fotovoltaicos", "sku": "KIT-RES-5.5KWP", "peso": 450.0, "dimensoes": "Pallet Padrão", "garantia": "Variável por componente", "images": ["produtos/kit_5_5kwp_main.png"], "stock": 10},
            {"name": "Kit Solar Off-Grid 1.0 kWp (Intelbras/Moura)", "description": "Solução autônoma para locais sem rede elétrica. Inclui painéis Intelbras, controlador e baterias Moura.", "preco": 12000.00, "categoria_slug": "kits_fotovoltaicos", "sku": "KIT-OFF-1.0KWP", "peso": 180.0, "dimensoes": "Pallet Médio", "garantia": "Variável por componente", "images": ["produtos/kit_offgrid_1kwp_main.png"], "stock": 5},
            
            # Estruturas e Cabos
            {"name": "Kit Estrutura Telha Fibrocimento", "description": "Fixação robusta e segura para telhados de fibrocimento.", "preco": 55.00, "categoria_slug": "estruturas_montagem", "sku": "ESTR-FIB-RET", "peso": 2.5, "dimensoes": "120x10x5cm", "garantia": "25 anos", "images": ["produtos/estrutura_fibrocimento_main.png"]},
            {"name": "Perfil Alumínio para Módulo Solar (3m)", "description": "Barra de alumínio de alta resistência para montagem de painéis.", "preco": 85.00, "categoria_slug": "estruturas_montagem", "sku": "PERF-AL-3M", "peso": 4.0, "dimensoes": "300x4x4cm", "garantia": "10 anos", "images": ["produtos/perfil_aluminio_main.png"], "stock": 500},
            {"name": "Cabo Solar Nexans EnergyFlex 6mm² Vermelho (100m)", "description": "Cabo fotovoltaico resistente a UV e intempéries.", "preco": 220.00, "categoria_slug": "acessorios", "sku": "CABO-SOLAR-6MM-VM", "peso": 4.5, "dimensoes": "Rolo 25x25cm", "garantia": "2 anos", "images": ["produtos/cabo_solar_6mm_main.png"], "stock": 100},
            {"name": "Conector MC4 Staubli EVO 2 (Par)", "description": "Conectores impermeáveis essenciais para a ligação de painéis.", "preco": 15.00, "categoria_slug": "acessorios", "sku": "CONN-MC4-PAIR", "peso": 0.08, "dimensoes": "Pequeno", "garantia": "1 ano", "images": ["produtos/mc4_pair_main.png"], "stock": 1000},
            
            # Ferramentas e Proteções
            {"name": "Testador de Painel Solar MPPT Tracker", "description": "Equipamento para análise de performance de painéis fotovoltaicos.", "preco": 1800.00, "categoria_slug": "ferramentas_instalacao", "sku": "TEST-MPPT", "peso": 1.5, "dimensoes": "20x15x5cm", "garantia": "1 ano", "images": ["produtos/mppt_tracker_main.png"], "stock": 5},
            {"name": "String Box Clamper Solar G3 (2 entradas)", "description": "Caixa de proteção para circuitos de corrente contínua.", "preco": 650.00, "categoria_slug": "acessorios", "sku": "STR-BX-CC2-WEG", "peso": 3.0, "dimensoes": "30x20x10cm", "garantia": "1 ano", "images": ["produtos/string_box_weg_main.png"], "stock": 30},
            {"name": "Medidor de Consumo Smart Wi-Fi (Intelbras)", "description": "Dispositivo para monitorar o consumo de energia da sua residência via aplicativo.", "preco": 300.00, "categoria_slug": "monitoramento", "sku": "INTEL-SMARTMET", "peso": 0.3, "dimensoes": "10x10x5cm", "garantia": "1 ano", "images": ["produtos/intelbras_smartmet_main.png"], "stock": 50},
        ]
        
        # Adicionar produtos genéricos para atingir o número desejado
        for i in range(max(0, self.num_produtos_adicionais - len(produtos_ecommerce_detalhes))):
            product_name = f"{fake.unique.catch_phrase()} Solar {random.choice(['Pro', 'Max', 'Light'])}"
            category_slug = random.choice(categorias_str)
            price = Decimal(random.uniform(50.00, 30000.00)).quantize(Decimal('0.01'))
            is_active_prod = fake.boolean(chance_of_getting_true=90)
            
            produtos_ecommerce_detalhes.append({
                "name": product_name,
                "description": fake.paragraph(nb_sentences=3, variable_nb_sentences=True),
                "preco": price,
                "categoria_slug": category_slug,
                "sku": fake.unique.ean13(),
                "stock": random.randint(0, 150) if is_active_prod else 0,
                "is_active": is_active_prod,
                "peso": round(random.uniform(0.1, 150.0), 2),
                "dimensoes": f"{random.randint(10,250)}x{random.randint(10,180)}x{random.randint(1,60)}cm",
                "garantia": f"{random.randint(1,25)} anos" if random.random() < 0.8 else None,
                "images": [f"produtos/generic_product_{random.randint(1,5)}.png"]
            })

        for prod_data in produtos_ecommerce_detalhes:
            try:
                produto, created = Produto.objects.get_or_create(sku=prod_data['sku'], defaults={
                    'name': prod_data['name'], 
                    'description': prod_data['description'],
                    'preco': Decimal(str(prod_data['preco'])).quantize(Decimal('0.01')), 
                    'categoria_id': prod_data['categoria_slug'], 
                    'stock': prod_data.get('stock', random.randint(5, 100)), 
                    'is_active': prod_data.get('is_active', True),
                    'peso': Decimal(str(prod_data.get('peso'))).quantize(Decimal('0.01')) if prod_data.get('peso') else None,
                    'dimensoes': prod_data.get('dimensoes'),
                    'garantia': prod_data.get('garantia'),
                })
                if created:
                    for i, image_path in enumerate(prod_data['images']):
                        ProdutoImage.objects.create(produto=produto, image=image_path, alt_text=f'Imagem de {produto.name}', is_main=(i == 0))
                    self.stdout.write(f'  - Produto E-commerce criado: {produto.name} (SKU: {produto.sku})')
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Erro de integridade ao criar Produto {prod_data.get('name', 'N/A')}: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro inesperado ao criar Produto {prod_data.get('name', 'N/A')}: {e}"))
        self.stdout.write(self.style.SUCCESS('\n--- Populacao de produtos e dados de e-commerce concluida. ---'))