# SysGov_Project/core/management/commands/import_data.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
import decimal

# Importe todos os modelos que você irá popular
from core.models import Processo, ETP, TR, Documento
from licitacoes.models import Edital, ResultadoLicitacao, Lote, ItemLicitado
from contratacoes.models import ItemCatalogo


class Command(BaseCommand):
    help = 'Importa dados completos de processos, documentos e licitações de uma pasta de arquivos CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            'pasta_de_importacao',
            type=str,
            help='O caminho para a pasta que contém os arquivos CSV de dados legados.',
        )

    def handle(self, *args, **options):
        pasta = options['pasta_de_importacao']
        self.stdout.write(self.style.WARNING(f'Iniciando a importação de dados da pasta: {pasta}'))
        
        if not os.path.isdir(pasta):
            raise CommandError(f"A pasta '{pasta}' não foi encontrada.")

        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            raise CommandError("Usuário 'admin' não encontrado. Por favor, crie um superusuário primeiro.")

        # Dicionários para mapear IDs legados para objetos do novo sistema
        processos_map = {}
        etps_map = {}
        trs_map = {}
        editais_map = {}
        catalogo_map = {}
        
        # --- Importação dos Processos (1º: Dependências principais) ---
        processos_importados = 0
        processos_erros = 0
        processos_csv_path = os.path.join(pasta, 'processos.csv')
        if os.path.exists(processos_csv_path):
            self.stdout.write(self.style.SUCCESS('\nImportando Processos...'))
            with open(processos_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            processo = Processo.objects.create(
                                usuario=admin_user,
                                titulo=row['titulo'],
                                descricao=row.get('descricao', ''),
                                numero_protocolo=row['numero_protocolo'],
                                status=row.get('status', 'EM_ELABORACAO'),
                                data_criacao=row.get('data_criacao'),
                            )
                            processos_map[row['id_legado']] = processo
                            processos_importados += 1
                            self.stdout.write(self.style.SUCCESS(f"  > Processo importado: {processo.numero_protocolo}"))
                    except Exception as e:
                        processos_erros += 1
                        self.stdout.write(self.style.ERROR(f"  > Erro ao importar Processo {row.get('numero_protocolo')}: {e}"))

        # --- Importação de Itens de Catálogo (2º: Outra dependência) ---
        catalogo_importados = 0
        catalogo_erros = 0
        catalogo_csv_path = os.path.join(pasta, 'catalogo_itens.csv')
        if os.path.exists(catalogo_csv_path):
            self.stdout.write(self.style.SUCCESS('\nImportando Itens de Catálogo...'))
            with open(catalogo_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            item = ItemCatalogo.objects.create(
                                nome_padronizado=row['nome_padronizado'],
                                unidade_medida=row['unidade_medida'],
                                descricao=row.get('descricao', ''),
                                preco_historico_medio=decimal.Decimal(row.get('preco_historico_medio', '0').replace(',', '.'))
                            )
                            catalogo_map[row['id_legado']] = item
                            catalogo_importados += 1
                            self.stdout.write(self.style.SUCCESS(f"  > Item de Catálogo importado: {item.nome_padronizado}"))
                    except Exception as e:
                        catalogo_erros += 1
                        self.stdout.write(self.style.ERROR(f"  > Erro ao importar Item de Catálogo '{row.get('nome_padronizado')}': {e}"))

        # --- Importação de ETPs (3º: Depende de Processos) ---
        etps_importados = 0
        etps_erros = 0
        etps_csv_path = os.path.join(pasta, 'etps.csv')
        if os.path.exists(etps_csv_path):
            self.stdout.write(self.style.SUCCESS('\nImportando ETPs...'))
            with open(etps_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            processo_vinculado = processos_map.get(row.get('id_processo_legado'))
                            if not processo_vinculado:
                                raise ObjectDoesNotExist(f"Processo legado ID '{row.get('id_processo_legado')}' não encontrado no mapeamento.")

                            etp = ETP.objects.create(
                                autor=admin_user,
                                processo_vinculado=processo_vinculado,
                                titulo=row['titulo'],
                                descricao_necessidade=row.get('descricao_necessidade', ''),
                                status=row.get('status', 'EM_ELABORACAO'),
                                data_criacao=row.get('data_criacao'),
                            )
                            etps_map[row['id_legado']] = etp
                            etps_importados += 1
                            self.stdout.write(self.style.SUCCESS(f"  > ETP importado: {etp.titulo}"))
                    except Exception as e:
                        etps_erros += 1
                        self.stdout.write(self.style.ERROR(f"  > Erro ao importar ETP '{row.get('titulo')}': {e}"))

        # --- Importação de TRs (4º: Depende de Processos) ---
        trs_importados = 0
        trs_erros = 0
        trs_csv_path = os.path.join(pasta, 'trs.csv')
        if os.path.exists(trs_csv_path):
            self.stdout.write(self.style.SUCCESS('\nImportando TRs...'))
            with open(trs_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            processo_vinculado = processos_map.get(row.get('id_processo_legado'))
                            if not processo_vinculado:
                                raise ObjectDoesNotExist(f"Processo legado ID '{row.get('id_processo_legado')}' não encontrado no mapeamento.")

                            tr = TR.objects.create(
                                autor=admin_user,
                                processo_vinculado=processo_vinculado,
                                titulo=row['titulo'],
                                objeto=row.get('objeto', ''),
                                status=row.get('status', 'EM_ELABORACAO'),
                                data_criacao=row.get('data_criacao'),
                            )
                            trs_map[row['id_legado']] = tr
                            trs_importados += 1
                            self.stdout.write(self.style.SUCCESS(f"  > TR importado: {tr.titulo}"))
                    except Exception as e:
                        trs_erros += 1
                        self.stdout.write(self.style.ERROR(f"  > Erro ao importar TR '{row.get('titulo')}': {e}"))

        # --- Importação de Editais (5º: Depende de Processos) ---
        editais_importados = 0
        editais_erros = 0
        editais_csv_path = os.path.join(pasta, 'editais.csv')
        if os.path.exists(editais_csv_path):
            self.stdout.write(self.style.SUCCESS('\nImportando Editais...'))
            with open(editais_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            processo_vinculado = processos_map.get(row.get('id_processo_legado'))
                            if not processo_vinculado:
                                raise ObjectDoesNotExist(f"Processo legado ID '{row.get('id_processo_legado')}' não encontrado no mapeamento.")

                            edital = Edital.objects.create(
                                processo_vinculado=processo_vinculado,
                                numero_edital=row['numero_edital'],
                                titulo=row['titulo'],
                                tipo_licitacao=row.get('tipo_licitacao', 'PREGAO'),
                                status=row.get('status', 'PUBLICADO'),
                                data_publicacao=row.get('data_publicacao'),
                                data_abertura_propostas=row.get('data_abertura_propostas'),
                                link_edital_completo=row.get('link_edital_completo', ''),
                            )
                            editais_map[row['id_legado']] = edital
                            editais_importados += 1
                            self.stdout.write(self.style.SUCCESS(f"  > Edital importado: {edital.numero_edital}"))
                    except Exception as e:
                        editais_erros += 1
                        self.stdout.write(self.style.ERROR(f"  > Erro ao importar Edital '{row.get('numero_edital')}': {e}"))
        
        # --- Importação de Resultados (6º: Depende de Editais) ---
        resultados_importados = 0
        resultados_erros = 0
        resultados_csv_path = os.path.join(pasta, 'resultados.csv')
        if os.path.exists(resultados_csv_path):
            self.stdout.write(self.style.SUCCESS('\nImportando Resultados de Licitação...'))
            with open(resultados_csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        with transaction.atomic():
                            edital_vinculado = editais_map.get(row.get('id_edital_legado'))
                            if not edital_vinculado:
                                raise ObjectDoesNotExist(f"Edital legado ID '{row.get('id_edital_legado')}' não encontrado no mapeamento.")

                            resultado = ResultadoLicitacao.objects.create(
                                edital=edital_vinculado,
                                data_homologacao=row.get('data_homologacao'),
                                fornecedor_vencedor=row['fornecedor_vencedor'],
                                valor_homologado=decimal.Decimal(row.get('valor_homologado', '0').replace(',', '.')),
                                economia_gerada=decimal.Decimal(row.get('economia_gerada', '0').replace(',', '.')),
                                link_documento_homologacao=row.get('link_documento_homologacao', '')
                            )
                            resultados_importados += 1
                            self.stdout.write(self.style.SUCCESS(f"  > Resultado importado para Edital {edital_vinculado.numero_edital}"))
                    except Exception as e:
                        resultados_erros += 1
                        self.stdout.write(self.style.ERROR(f"  > Erro ao importar Resultado '{row.get('id_edital_legado')}': {e}"))
        
        # --- Resumo Final ---
        self.stdout.write(self.style.SUCCESS(f'\n--- Resumo da Importação ---'))
        self.stdout.write(f'  - Processos: {processos_importados} importados ({processos_erros} erros)')
        self.stdout.write(f'  - Itens de Catálogo: {catalogo_importados} importados ({catalogo_erros} erros)')
        self.stdout.write(f'  - ETPs: {etps_importados} importados ({etps_erros} erros)')
        self.stdout.write(f'  - TRs: {trs_importados} importados ({trs_erros} erros)')
        self.stdout.write(f'  - Editais: {editais_importados} importados ({editais_erros} erros)')
        self.stdout.write(f'  - Resultados: {resultados_importados} importados ({resultados_erros} erros)')
        
        if any([processos_erros, catalogo_erros, etps_erros, trs_erros, editais_erros, resultados_erros]):
            self.stdout.write(self.style.ERROR(f'  - Importação concluída com erros. Verifique os logs acima.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  - Importação concluída com sucesso!'))