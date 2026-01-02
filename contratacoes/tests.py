# contratacoes/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal # Para o tipo DecimalField
from .models import ETP, TR
# Precisaremos importar Forms e Views quando criá-los
# from .forms import ETPForm, TRForm
# from .views import criar_etp, detalhar_etp # Exemplo


# Obtém o modelo de usuário do Django
User = get_user_model()

# --- Testes de Modelos (Model Tests) ---

class ETPModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Configurações de dados que serão usadas por todos os métodos de teste
        # Cria um usuário para ser o autor
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        # Cria um ETP de exemplo
        cls.etp = ETP.objects.create(
            titulo="Aquisição de Material de Escritório",
            numero_processo="PROCESSO-001/2025",
            setor_demandante="Departamento de Compras",
            autor=cls.user,
            descricao_necessidade="Falta de suprimentos básicos.",
            objetivo_contratacao="Garantir o fluxo de trabalho.",
            requisitos_contratacao="Qualidade padrão e durabilidade.",
            levantamento_solucoes_mercado="Vários fornecedores.",
            estimativa_quantidades="Consumo anual estimado.",
            estimativa_valor=Decimal('50000.00'),
            resultados_esperados="Eficiência no dia a dia.",
            viabilidade_justificativa_solucao="Solução mais econômica e eficiente.",
            alinhamento_planejamento="Conforme plano estratégico."
        )

    def test_etp_creation(self):
        # Verifica se o ETP foi criado corretamente no banco de dados
        self.assertEqual(ETP.objects.count(), 1)
        etp = ETP.objects.get(id=self.etp.id)
        self.assertEqual(etp.titulo, "Aquisição de Material de Escritório")
        self.assertEqual(etp.numero_processo, "PROCESSO-001/2025")
        self.assertEqual(etp.autor, self.user)
        self.assertEqual(etp.status, 'EM_ELABORACAO') # Default status

    def test_etp_str_method(self):
        # Verifica se o método __str__ do modelo retorna o esperado
        etp = ETP.objects.get(id=self.etp.id)
        self.assertEqual(str(etp), "ETP: Aquisição de Material de Escritório (PROCESSO-001/2025)")

    def test_etp_fields_verbose_name(self):
        # Verifica os verbose_name dos campos
        etp = ETP.objects.get(id=self.etp.id)
        field_label = etp._meta.get_field('titulo').verbose_name
        self.assertEqual(field_label, 'Título do ETP')
        field_label = etp._meta.get_field('estimativa_valor').verbose_name
        self.assertEqual(field_label, '6. Estimativa do Valor da Contratação (R$)')

    def test_etp_unique_numero_processo(self):
        # Testa a unicidade do numero_processo
        with self.assertRaises(Exception): # Espera que uma exceção seja levantada
            ETP.objects.create(
                titulo="Outro ETP",
                numero_processo="PROCESSO-001/2025", # Mesmo número de processo
                setor_demandante="Outro Setor",
                autor=self.user,
                descricao_necessidade="xyz",
                objetivo_contratacao="xyz",
                requisitos_contratacao="xyz",
                levantamento_solucoes_mercado="xyz",
                estimativa_quantidades="xyz",
                estimativa_valor=Decimal('100.00'),
                resultados_esperados="xyz",
                viabilidade_justificativa_solucao="xyz",
                alinhamento_planejamento="xyz"
            )

class TRModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser_tr',
            password='testpassword_tr'
        )
        cls.etp = ETP.objects.create(
            titulo="Contratação de Sistema GED",
            numero_processo="PROCESSO-002/2025",
            setor_demandante="Departamento de TI",
            autor=cls.user,
            descricao_necessidade="Necessidade de sistema para documentos.",
            objetivo_contratacao="Implementar GED.",
            requisitos_contratacao="Digitalização e workflow.",
            levantamento_solucoes_mercado="Softwares de mercado.",
            estimativa_quantidades="Para 200 usuários.",
            estimativa_valor=Decimal('950000.00'),
            resultados_esperados="Otimização de processos.",
            viabilidade_justificativa_solucao="Solução de prateleira.",
            alinhamento_planejamento="Transformação digital."
        )
        cls.tr = TR.objects.create(
            etp_origem=cls.etp,
            titulo="Termo de Referência para Sistema GED",
            numero_processo="TR-001/2025",
            autor=cls.user,
            objeto="Sistema de Gestão Eletrônica de Documentos.",
            justificativa="Modernizar a gestão documental.",
            especificacoes_tecnicas="Módulos de protocolo, tramitação, etc.",
            prazo_execucao_entrega="120 dias.",
            criterios_habilitacao="Atestados de capacidade técnica.",
            criterios_aceitacao="Testes de funcionalidade.",
            criterios_pagamento="Parcelas mensais.",
            obrigacoes_partes="Definição de responsabilidades.",
            sancoes_administrativas="Multas e rescisão.",
            fiscalizacao_contrato="Fiscal técnico e administrativo.",
            vigencia_contrato="24 meses.",
            estimativa_preco_tr=Decimal('950000.00')
        )

    def test_tr_creation(self):
        # Verifica se o TR foi criado corretamente
        self.assertEqual(TR.objects.count(), 1)
        tr = TR.objects.get(id=self.tr.id)
        self.assertEqual(tr.titulo, "Termo de Referência para Sistema GED")
        self.assertEqual(tr.etp_origem, self.etp)
        self.assertEqual(tr.status, 'EM_ELABORACAO')

    def test_tr_str_method(self):
        # Verifica o método __str__ do TR
        tr = TR.objects.get(id=self.tr.id)
        self.assertEqual(str(tr), "TR: Termo de Referência para Sistema GED (ETP: PROCESSO-002/2025)")

    def test_tr_relationship_to_etp(self):
        # Verifica a relação OneToOne entre TR e ETP
        tr = TR.objects.get(id=self.tr.id)
        self.assertEqual(tr.etp_origem.titulo, "Contratação de Sistema GED")
        self.assertEqual(self.etp.termo_referencia, tr) # Verifica o related_name

