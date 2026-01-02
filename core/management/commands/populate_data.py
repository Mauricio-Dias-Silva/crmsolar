import random
from faker import Faker
from decimal import Decimal
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction

# Importações dos modelos
from django.contrib.auth.models import User, Group
from core.models import Processo, Fornecedor
from contratacoes.models import PCA, ItemPCA, ETP, TR, Contrato, AtaRegistroPrecos
from licitacoes.models import Edital, ItemLicitado, Pregao, ParticipanteLicitacao, Lance, ResultadoLicitacao
from financeiro.models import NotaEmpenho, DocumentoFiscal, Pagamento

class Command(BaseCommand):
    help = 'Popula a base de dados com dados de teste realistas para múltiplos utilizadores.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a população da base de dados...")
        
        with transaction.atomic():
            self.limpar_dados()
            self.criar_grupos_e_usuarios()
            # Criamos vários cenários para garantir dados para os gráficos
            for i in range(15):
                self.stdout.write(f"\n--- Criando cenário de licitação completo {i+1}/15 ---")
                self.criar_cenario_completo()
        
        self.stdout.write(self.style.SUCCESS("\nPopulação de dados concluída com sucesso!"))

    def limpar_dados(self):
        self.stdout.write("  Deletando dados antigos...")
        Pagamento.objects.all().delete()
        DocumentoFiscal.objects.all().delete()
        NotaEmpenho.objects.all().delete()
        AtaRegistroPrecos.objects.all().delete()
        Contrato.objects.all().delete()
        Lance.objects.all().delete()
        ParticipanteLicitacao.objects.all().delete()
        Pregao.objects.all().delete()
        ResultadoLicitacao.objects.all().delete()
        ItemLicitado.objects.all().delete()
        Edital.objects.all().delete()
        TR.objects.all().delete()
        ETP.objects.all().delete()
        ItemPCA.objects.all().delete()
        PCA.objects.all().delete()
        Processo.objects.all().delete()
        Fornecedor.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Group.objects.all().delete()
        self.stdout.write("  Limpeza concluída.")

    def criar_grupos_e_usuarios(self):
        self.stdout.write("  Criando grupos e utilizadores de teste...")
        fake = Faker('pt_BR')
        grupos_nomes = ['Analise de Requerimentos', 'Setor de Orcamento', 'Comissao de Licitacao']
        for nome in grupos_nomes:
            Group.objects.get_or_create(name=nome)
        
        for nome_grupo in grupos_nomes:
            grupo = Group.objects.get(name=nome_grupo)
            username = nome_grupo.lower().replace(' ', '_').replace('ç', 'c').replace('ã', 'a')
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='123', email=fake.email())
                user.groups.add(grupo)

        grupo_secretarias, _ = Group.objects.get_or_create(name='Secretarias')
        for i in range(1, 4):
            username = f'secretaria_{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password='123', email=fake.email())
                user.groups.add(grupo_secretarias)

    def criar_cenario_completo(self):
        fake = Faker('pt_BR')
        autores_possiveis = User.objects.filter(groups__name='Secretarias')
        autor_do_processo = random.choice(autores_possiveis)
        analise_user = User.objects.get(username='analise_de_requerimentos')
        pregoeiro_user = User.objects.get(username='comissao_de_licitacao')
        
        # --- CORREÇÃO AQUI: Trocado 'raza_social' por 'razao_social' ---
        fornecedores = [Fornecedor.objects.create(razao_social=fake.company(), cnpj=fake.cnpj()) for _ in range(3)]

        pca, _ = PCA.objects.get_or_create(ano_vigencia=timezone.now().year, defaults={'data_aprovacao': timezone.now().date(), 'responsavel_aprovacao': pregoeiro_user})
        item_pca = ItemPCA.objects.create(pca=pca, identificador_item=f"ITEM-{pca.ano_vigencia}-{random.randint(1000, 9999)}", descricao_item=fake.sentence(nb_words=6), valor_estimado_pca=Decimal(random.uniform(20000, 80000)), unidade_requisitante="Secretaria Aleatória")
        processo = Processo.objects.create(usuario=autor_do_processo, titulo=f"Aquisição de {fake.bs()}", numero_protocolo=f"{random.randint(1000, 9999)}/{timezone.now().year}")
        status_escolhido = random.choice(['EM_ELABORACAO', 'AGUARDANDO_ANALISE', 'AGUARDANDO_ORCAMENTO', 'APROVADO'])
        etp = ETP.objects.create(processo_vinculado=processo, titulo=f"ETP para {processo.titulo}", numero_processo=processo.numero_protocolo, setor_demandante="Educação", autor=autor_do_processo, descricao_necessidade=fake.paragraph(), objetivo_contratacao=fake.paragraph(), requisitos_contratacao=fake.paragraph(), estimativa_quantidades="100 unidades", estimativa_valor=item_pca.valor_estimado_pca, status=status_escolhido)

        if etp.status == 'APROVADO':
            tr = TR.objects.create(etp_origem=etp, processo_vinculado=processo, titulo=f"TR para {etp.titulo}", numero_processo=processo.numero_protocolo, autor=analise_user, objeto=etp.objetivo_contratacao, status='APROVADO')
            edital = Edital.objects.create(processo_vinculado=processo, numero_edital=f"{random.randint(1, 100)}/{timezone.now().year}", titulo=tr.objeto, data_publicacao=timezone.now().date(), data_abertura_propostas=timezone.now() + timezone.timedelta(days=15), status='PUBLICADO', valor_estimado=etp.estimativa_valor)
            item_licitado = ItemLicitado.objects.create(edital=edital, descricao_item=tr.objeto, quantidade=100, unidade_medida="Unidade")
            pregao = Pregao.objects.create(edital=edital, pregoeiro=pregoeiro_user, data_abertura_sessao=edital.data_abertura_propostas, status='FINALIZADO', data_encerramento_sessao=timezone.now())
            participantes = [ParticipanteLicitacao.objects.create(pregao=pregao, fornecedor=forn) for forn in fornecedores]
            lances = [Lance.objects.create(participante=p, item=item_licitado, valor_lance=etp.estimativa_valor * Decimal(random.uniform(0.7, 1.1))) for p in participantes]
            lance_vencedor = min(lances, key=lambda x: x.valor_lance)
            lance_vencedor.aceito = True
            lance_vencedor.save()
            fornecedor_vencedor = lance_vencedor.participante.fornecedor
            ResultadoLicitacao.objects.create(edital=edital, item_licitado=item_licitado, fornecedor_vencedor=fornecedor_vencedor.razao_social, cnpj_vencedor=fornecedor_vencedor.cnpj, valor_homologado=lance_vencedor.valor_lance, data_homologacao=timezone.now().date(), responsavel_registro=pregoeiro_user, valor_estimado_inicial=edital.valor_estimado)

            if random.choice([True, False]):
                contrato = Contrato.objects.create(processo_vinculado=processo, licitacao_origem=edital, contratado=fornecedor_vencedor, numero_contrato=f"CT-{random.randint(1000, 9999)}", ano_contrato=timezone.now().year, objeto=edital.titulo, valor_total=lance_vencedor.valor_lance, data_assinatura=timezone.now().date(), data_inicio_vigencia=timezone.now().date(), data_fim_vigencia=timezone.now().date() + timezone.timedelta(days=365))
                doc_fiscal = DocumentoFiscal.objects.create(processo_vinculado=processo, contrato_vinculado=contrato, fornecedor=fornecedor_vencedor, documento_fiscal_numero=f"NF-{random.randint(1000, 9999)}", documento_fiscal_valor=contrato.valor_total, documento_fiscal_data_emissao=timezone.now().date())
                NotaEmpenho.objects.create(contrato=contrato, fornecedor=fornecedor_vencedor, numero_empenho=f"NE-{random.randint(1000, 9999)}", ano_empenho=timezone.now().year, data_emissao=timezone.now().date(), valor=doc_fiscal.documento_fiscal_valor, descricao=f"Empenho para NF {doc_fiscal.documento_fiscal_numero}")
                Pagamento.objects.create(documento_fiscal=doc_fiscal, nota_fiscal_valor_pago=doc_fiscal.documento_fiscal_valor, nota_fiscal_pagto_dt=timezone.now().date() + timezone.timedelta(days=random.randint(5, 25)))
            else:
                AtaRegistroPrecos.objects.create(processo_vinculado=processo, licitacao_origem=edital, fornecedor_beneficiario=fornecedor_vencedor, numero_ata=f"ARP-{random.randint(100, 999)}", ano_ata=timezone.now().year, objeto=edital.titulo, valor_total_registrado=lance_vencedor.valor_lance, data_assinatura=timezone.now().date(), data_inicio_vigencia=timezone.now().date(), data_fim_vigencia=timezone.now().date() + timezone.timedelta(days=365))

