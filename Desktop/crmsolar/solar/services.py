import csv
import os
import decimal
import logging
import io
import base64
import requests
from django.conf import settings

# --- CONFIGURAÇÕES ---
logger = logging.getLogger(__name__)
PERDA_SISTEMA = decimal.Decimal('0.78')
TARIFA_MEDIA_KWH = decimal.Decimal('0.90')

# --- 1. LÓGICA DE CARREGAMENTO CSV (IRRADIAÇÃO) ---
IRRADIAÇÃO_POR_MUNICIPIO = {}
def _carregar_irradiacao():
    global IRRADIAÇÃO_POR_MUNICIPIO
    if IRRADIAÇÃO_POR_MUNICIPIO:
        return
    caminho_csv = os.path.join(os.path.dirname(__file__), 'dados_irradiacao.csv')
    try:
        with open(caminho_csv, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cidade = row['cidade'].strip().upper()
                uf = row['uf'].strip().upper()
                IRRADIAÇÃO_POR_MUNICIPIO[(cidade, uf)] = decimal.Decimal(row['irradiacao'])
    except Exception as e:
        logger.error(f"Erro ao carregar CSV de irradiacao: {e}")

def get_solar_irradiation(cidade=None, uf=None):
    _carregar_irradiacao()
    def safe_str(value):
        if value is None: return ""
        if isinstance(value, (float, decimal.Decimal)): return str(value)
        return str(value).strip()
    cidade_str = safe_str(cidade).upper()
    uf_str = safe_str(uf).upper()
    if cidade_str and uf_str:
        return IRRADIAÇÃO_POR_MUNICIPIO.get((cidade_str, uf_str), decimal.Decimal(5.0))
    return decimal.Decimal(5.0)

# --- 2. LÓGICA FINANCEIRA ---
def calculate_financial_metrics(projeto):
    if not projeto.irradiacao_media_diaria or not projeto.potencia_kwp or not projeto.valor_total:
        return None
    try:
        irradiacao = projeto.irradiacao_media_diaria
        potencia = projeto.potencia_kwp
        valor_total = projeto.valor_total
        geracao_diaria = potencia * irradiacao * PERDA_SISTEMA
        geracao_mensal = geracao_diaria * decimal.Decimal(30.5)
        economia_mensal = geracao_mensal * TARIFA_MEDIA_KWH
        economia_anual = economia_mensal * 12
        payback_anos = valor_total / economia_anual if economia_anual > 0 else decimal.Decimal(0)
        return {
            'geracao_mensal': geracao_mensal.quantize(decimal.Decimal('0.1')),
            'economia_mensal': economia_mensal.quantize(decimal.Decimal('0.01')),
            'payback_anos': payback_anos.quantize(decimal.Decimal('0.1'))
        }
    except Exception as e:
        logger.error(f"ERRO CÁLCULO FINANCEIRO: {e}")
        return None

# --- 3. LÓGICA DE GRÁFICO (MATPLOTLIB) ---
def generate_savings_chart_base64(economia_mensal):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None
    try:
        anos = np.arange(1, 6)
        economia_acumulada = [(economia_mensal * 12 * ano) for ano in anos]
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar(anos, economia_acumulada, color='#34A853')
        ax.set_title('Economia Acumulada Estimada (5 Anos)', fontsize=10)
        ax.set_xlabel('Ano')
        ax.set_ylabel('Economia Acumulada (R$)')
        ax.ticklabel_format(style='plain', axis='y')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()
    except Exception as e:
        logger.error(f"ERRO NA GERAÇÃO DO GRÁFICO: {e}")
        return None

# --- 4. LÓGICA DE TEXTO IA (VERSÃO FINAL POLIDA) ---
def generate_ai_analysis(projeto_data):
    """Gera uma análise completa e persuasiva, limpando os títulos da resposta."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return {'resumo': "A IA não está configurada (API Key não encontrada).", 'explicacao': "", 'faq': ""}

    model_name = "models/gemini-2.5-flash-preview-05-20"
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"

    prompt = f"""
    Aja como um consultor sênior de energia solar criando uma análise para uma proposta comercial.
    O cliente é '{projeto_data.get('cliente', 'Valioso Cliente')}'.
    Os dados do projeto são:
    - Potência: {projeto_data.get('kwp', 'N/A')} kWp
    - Economia Mensal Estimada: R$ {projeto_data.get('economia', 'N/A')}
    - Payback (Retorno do Investimento): {projeto_data.get('payback', 'N/A')} anos

    Gere o conteúdo para as seguintes seções, usando os títulos exatamente como estão, separados por '---'.

    # RESUMO EXECUTIVO
    (Escreva um parágrafo conciso e impactante resumindo o projeto como um excelente investimento financeiro e sustentável para o cliente.)
    ---
    # TRADUZINDO OS NÚMEROS
    (Explique de forma simples o que significa a 'Potência em kWp' e o 'Payback', focando nos benefícios práticos para o dia a dia do cliente.)
    ---
    # PERGUNTAS FREQUENTES
    (Crie 2 perguntas que um cliente provavelmente faria sobre este projeto e responda-as de forma clara. Ex: 'E em dias nublados?' ou 'A manutenção é cara?')
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload, timeout=45)
        response.raise_for_status()
        data = response.json()
        full_text = data['candidates'][0]['content']['parts'][0]['text']

        # 💡 LÓGICA DE LIMPEZA MELHORADA E FINAL
        parts = full_text.split('---')
        
        # Pega a primeira parte, remove o título e limpa espaços em branco
        resumo = parts[0].replace("# RESUMO EXECUTIVO", "").strip()
        
        # Faz o mesmo para as outras partes, com verificação para evitar erros
        explicacao = parts[1].replace("# TRADUZINDO OS NÚMEROS", "").strip() if len(parts) > 1 else ""
        faq = parts[2].replace("# PERGUNTAS FREQUENTES", "").strip() if len(parts) > 2 else ""

        return {'resumo': resumo, 'explicacao': explicacao, 'faq': faq}

    except Exception as e:
        logger.error(f"ERRO API GEMINI (Análise Completa): {e}")
        return {
            'resumo': "Não foi possível gerar a análise inteligente neste momento.",
            'explicacao': "Por favor, verifique se todos os dados do projeto (potência, valor, irradiação) estão preenchidos corretamente.",
            'faq': ""
        }

