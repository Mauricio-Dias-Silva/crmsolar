import csv
import os
import decimal
import logging
import io
import base64
from collections import defaultdict

# Imports opcionais para garantir que o app não quebre se não estiverem instalados
try:
    import google.generai as genai
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    genai = None
    plt = None
    np = None

logger = logging.getLogger(__name__)

# --- 1. LÓGICA DE CARREGAMENTO DE DADOS DE IRRADIAÇÃO (CSV) ---

IRRADIAÇÃO_POR_MUNICIPIO = {}

def _carregar_irradiacao():
    """Carrega dados de irradiação de um CSV para a memória, executando apenas uma vez."""
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
    except FileNotFoundError:
        logger.error(f"Arquivo 'dados_irradiacao.csv' não encontrado em {caminho_csv}")
    except Exception as e:
        logger.error(f"Erro ao carregar CSV de irradiacao: {e}")

def get_solar_irradiation(cidade=None, uf=None):
    """Retorna irradiação solar média diária (kWh/m²/dia) com base na cidade/UF."""
    _carregar_irradiacao()
    
    def safe_str(value):
        return "" if value is None else str(value).strip()

    cidade_str = safe_str(cidade).upper()
    uf_str = safe_str(uf).upper()

    if cidade_str and uf_str:
        chave = (cidade_str, uf_str)
        return IRRADIAÇÃO_POR_MUNICIPIO.get(chave, decimal.Decimal('5.0'))
    
    return decimal.Decimal('5.0')


# --- 2. LÓGICA DE CÁLCULOS FINANCEIROS ---

PERDA_SISTEMA = decimal.Decimal('0.78') 
TARIFA_MEDIA_KWH = decimal.Decimal('0.90')

def calculate_financial_metrics(projeto):
    """Calcula a geração mensal, economia e payback do projeto."""
    if not all([projeto.irradiacao_media_diaria, projeto.potencia_kwp, projeto.valor_total]):
        return None 
        
    try:
        irradiacao = decimal.Decimal(projeto.irradiacao_media_diaria)
        potencia = decimal.Decimal(projeto.potencia_kwp)
        valor_total = decimal.Decimal(projeto.valor_total)
        
        geracao_diaria = potencia * irradiacao * PERDA_SISTEMA
        geracao_mensal = geracao_diaria * decimal.Decimal('30.5') 
        
        economia_mensal = geracao_mensal * TARIFA_MEDIA_KWH
        economia_anual = economia_mensal * 12
        
        payback_anos = valor_total / economia_anual if economia_anual > 0 else decimal.Decimal('0')
        
        return {
            'geracao_mensal': geracao_mensal.quantize(decimal.Decimal('0.1')),
            'economia_mensal': economia_mensal.quantize(decimal.Decimal('0.01')),
            'payback_anos': payback_anos.quantize(decimal.Decimal('0.1'))
        }
    except Exception as e:
        logger.error(f"ERRO CÁLCULO FINANCEIRO: {e}")
        return None


# --- 3. LÓGICA DE GERAÇÃO DE GRÁFICO ---

def generate_savings_chart_base64(economia_mensal):
    """Cria um gráfico de barras de economia acumulada e o retorna como Base64."""
    if not all([plt, np, economia_mensal]):
        return None
        
    try:
        anos = np.arange(1, 6)
        economia_acumulada = [float(economia_mensal * 12 * ano) for ano in anos]

        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(8, 4))
        
        bars = ax.bar(anos, economia_acumulada, color='#34A853')
        ax.set_title('Projeção de Economia Acumulada (5 Anos)', fontsize=12)
        ax.set_xlabel('Ano do Investimento')
        ax.set_ylabel('Economia Acumulada (R$)')
        ax.set_xticks(anos)
        ax.ticklabel_format(style='plain', axis='y')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close(fig)
        
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        return img_base64
    except Exception as e:
        logger.error(f"ERRO NA GERAÇÃO DO GRÁFICO: {e}")
        return None


# --- 4. LÓGICA DE GERAÇÃO DE TEXTO COM IA ---

def generate_sales_pitch(projeto_data):
    """Gera um texto de vendas persuasivo usando a API Gemini."""
    if not genai:
        return "A integração com a IA para geração de texto não está configurada neste ambiente."

    # Prompt melhorado para um texto mais completo e personalizado
    prompt = f"""
    Aja como um especialista em vendas de energia solar.
    Escreva um parágrafo curto e persuasivo para uma proposta comercial para o cliente '{projeto_data.get('cliente', 'Valioso Cliente')}'.
    Destaque os seguintes benefícios de forma clara e direta:
    - O sistema solar tem {projeto_data.get('kwp', 'uma potência ideal')} kWp.
    - A economia mensal estimada é de R$ {projeto_data.get('economia', 'um valor significativo')}.
    - O retorno sobre o investimento (ROI) é excelente.
    Use uma linguagem positiva, focada em independência energética e valorização do imóvel.
    Seja conciso e profissional.
    """
    
    try:
        # Lembre-se de configurar sua API Key do Gemini nas variáveis de ambiente
        # genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"ERRO API GEMINI: {e}")
        return "Investir em energia solar é dar um passo rumo à independência energética e à sustentabilidade. Com este sistema, você reduzirá drasticamente sua conta de luz e valorizará seu imóvel, garantindo um futuro mais econômico e ecológico."

