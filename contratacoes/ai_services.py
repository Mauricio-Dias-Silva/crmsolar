
import google.generativeai as genai
from decouple import config
import re

# --- ETAPA 2: CONFIGURAÇÃO DA API KEY ---
GOOGLE_API_KEY = config('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


# --- FUNÇÃO 1: GERAR RASCUNHO DO ETP ---
def gerar_rascunho_etp_com_ia(descricao_necessidade):
    """
    Recebe a descrição da necessidade do usuário e usa a IA para gerar um
    rascunho estruturado para um Estudo Técnico Preliminar (ETP).
    """
    prompt = f"""
    Você é um especialista em licitações e contratos da administração pública brasileira.
    Sua tarefa é criar um rascunho detalhado para um Estudo Técnico Preliminar (ETP) com base na necessidade descrita.
    A resposta deve ser um texto claro e bem estruturado, dividido EXATAMENTE nas seções a seguir. Preencha cada seção da melhor forma possível.

    Necessidade Descrita pelo Usuário: "{descricao_necessidade}"

    --- Rascunho do ETP ---

    **TÍTULO SUGERIDO:**
    [Crie um título claro e objetivo para o ETP com base na necessidade]

    **SETOR DEMANDANTE SUGERIDO:**
    [Se a necessidade mencionar um setor (ex: saúde, educação), coloque-o aqui. Senão, deixe em branco.]

    **1. DESCRIÇÃO DA NECESSIDADE:**
    [Elabore aqui uma descrição formal da necessidade]

    **2. OBJETIVO DA CONTRATAÇÃO:**
    [Descreva aqui qual o resultado esperado com a contratação]

    **3. REQUISITOS DA CONTRATAÇÃO:**
    [Liste aqui os requisitos essenciais do objeto a ser contratado]

    **4. LEVANTAMENTO DE SOLUÇÕES DE MERCADO:**
    [Descreva brevemente as possíveis soluções que existem no mercado]

    **5. ESTIMATIVA DAS QUANTIDADES:**
    [Forneça uma estimativa inicial da quantidade necessária, justificando o cálculo]

    **6. ESTIMATIVA DO VALOR DA CONTRATAÇÃO (R$):**
    [Forneça uma estimativa de custo bem fundamentada, sugerindo fontes para pesquisa de preço. NÃO coloque um valor numérico final, apenas o texto da estimativa.]

    **7. RESULTADOS ESPERADOS:**
    [Detalhe os benefícios que a administração pública terá com esta contratação]

    **8. VIABILIDADE E JUSTIFICATIVA DA SOLUÇÃO ESCOLHIDA:**
    [Argumente por que a solução proposta é a mais viável para a administração]
    
    **10. ALINHAMENTO COM O PLANEJAMENTO ESTRATÉGICO:**
    [Elabore um texto justificando como esta contratação se alinha com objetivos maiores da instituição, como modernização, eficiência, melhoria de serviços públicos e valorização de servidores.]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com o serviço de IA: {e}"


# --- FUNÇÃO 2: PROCESSAR O RASCUNHO DO ETP ---
def parse_rascunho_etp(rascunho_texto):
    """
    Recebe o texto bruto gerado pela IA e o transforma em um dicionário
    mapeado para os campos do modelo ETP.
    """
    dados_etp = {}
    padrao = r"\*\*(?:\d+\.\s*)?([^:]+):\*\*\s*(.*?)(?=\n\*\*\s*[\d\w]|\Z)"
    partes = re.findall(padrao, rascunho_texto, re.DOTALL)

    # Corrigido o mapeamento do campo de estimativa de valor para o campo correto
    mapa_campos = {
        'TÍTULO SUGERIDO': 'titulo',
        'SETOR DEMANDANTE SUGERIDO': 'setor_demandante',
        'DESCRIÇÃO DA NECESSIDADE': 'descricao_necessidade',
        'OBJETIVO DA CONTRATAÇÃO': 'objetivo_contratacao',
        'REQUISITOS DA CONTRATAÇÃO': 'requisitos_contratacao',
        'LEVANTAMENTO DE SOLUÇÕES DE MERCADO': 'levantamento_solucoes_mercado',
        'ESTIMATIVA DAS QUANTIDADES': 'estimativa_quantidades',
        'ESTIMATIVA DO VALOR DA CONTRATAÇÃO (R$)': 'estimativa_valor', # <<< CORRIGIDO
        'RESULTADOS ESPERADOS': 'resultados_esperados',
        'VIABILIDADE E JUSTIFICATIVA DA SOLUÇÃO ESCOLHIDA': 'viabilidade_justificativa_solucao',
        'ALINHAMENTO COM O PLANEJAMENTO ESTRATÉGICO': 'alinhamento_planejamento',
    }

    for titulo, conteudo in partes:
        titulo_limpo = titulo.strip().upper()
        if titulo_limpo in mapa_campos:
            campo_modelo = mapa_campos[titulo_limpo]
            if campo_modelo not in dados_etp:
                dados_etp[campo_modelo] = conteudo.strip()

    return dados_etp


# --- FUNÇÃO 3: GERAR RASCUNHO DO TR (VERSÃO ATUALIZADA E MAIS COMPLETA) ---
def gerar_rascunho_tr_com_ia(texto_etp_aprovado):
    """
    Recebe o texto de um ETP aprovado e usa a IA para gerar um
    rascunho MUITO MAIS COMPLETO para um Termo de Referência (TR).
    """
    prompt = f"""
    Você é um especialista em licitações e contratos da administração pública brasileira.
    Sua tarefa é atuar como um analista de requerimentos e criar um rascunho detalhado para um Termo de Referência (TR) com base no Estudo Técnico Preliminar (ETP) que foi aprovado.

    A resposta deve ser um documento formal, claro e bem estruturado, dividido nas seções de um TR padrão. Use as informações do ETP abaixo para preencher cada seção da melhor forma possível. Para seções mais burocráticas (obrigações, sanções, fiscalização), gere um texto padrão e juridicamente sólido.

    --- ETP Aprovado (Fonte de Dados) ---
    {texto_etp_aprovado}
    --- Fim do ETP ---

    --- Rascunho do Termo de Referência (TR) ---

    **1. OBJETO:**
    [Com base no ETP, descreva de forma clara e concisa o que será contratado.]

    **2. JUSTIFICATIVA E OBJETIVOS DA CONTRATAÇÃO:**
    [Use a justificativa e os objetivos do ETP para elaborar este campo.]

    **3. ESPECIFICAÇÕES TÉCNICAS E REQUISITOS:**
    [Detalhe aqui as características técnicas, funcionais e de qualidade do bem ou serviço, usando os requisitos definidos no ETP como base.]
    
    **4. PRAZO DE EXECUÇÃO/ENTREGA:**
    [Sugira um prazo de entrega ou execução razoável para o objeto descrito.]

    **5. CRITÉRIOS DE ACEITAÇÃO DO OBJETO:**
    [Descreva como a administração irá verificar se o que foi entregue está de acordo com o que foi solicitado nas especificações.]

    **6. OBRIGAÇÕES DA CONTRATADA E DA CONTRATANTE:**
    [Gere um texto padrão com as principais obrigações de ambas as partes em um contrato público.]
    
    **7. SANÇÕES ADMINISTRATIVAS:**
    [Gere um texto padrão citando as possíveis sanções em caso de descumprimento contratual, com base na Lei 14.133/21.]
    
    **8. FISCALIZAÇÃO DO CONTRATO:**
    [Gere um texto padrão descrevendo o papel do fiscal do contrato e a forma como a fiscalização será conduzida.]
    
    **9. VIGÊNCIA DO CONTRATO:**
    [Sugira um prazo de vigência padrão para este tipo de contrato (ex: 12 meses).]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com o serviço de IA: {e}"


def parse_rascunho_tr(rascunho_texto):
    # ... (código existente)
    mapa_campos = {
        'OBJETO': 'objeto',
        'JUSTIFICATIVA E OBJETIVOS DA CONTRATAÇÃO': 'justificativa',
        'ESPECIFICAÇÕES TÉCNICAS E REQUISITOS': 'especificacoes_tecnicas',
        'PRAZO DE EXECUÇÃO/ENTREGA': 'prazo_execucao_entrega',
        'CRITÉRIOS DE ACEITAÇÃO DO OBJETO': 'criterios_aceitacao',
        'OBRIGAÇÕES DA CONTRATADA E DA CONTRATANTE': 'obrigacoes_partes',
        'SANÇÕES ADMINISTRATIVAS': 'sancoes_administrativas',
        'FISCALIZAÇÃO DO CONTRATO': 'fiscalizacao_contrato',
        'VIGÊNCIA DO CONTRATO': 'vigencia_contrato',
        
        # Novas seções do seu modelo TR
        'METODOLOGIA DE EXECUÇÃO (SE SERVIÇO)': 'metodologia_execucao',
        'CRONOGRAMA FÍSICO-FINANCEIRO (SE APLICÁVEL)': 'cronograma_fisico_financeiro',
        'CRITÉRIOS DE HABILITAÇÃO (TÉCNICA)': 'criterios_habilitacao',
        'CRITÉRIOS DE PAGAMENTO': 'criterios_pagamento',
        'ESTIMATIVA DE PREÇO (R$)': 'estimativa_preco_tr', # Atenção: a IA não gera números.
    }
    
    # ... (código para preencher o dicionário)
    return dados_tr

def analisar_contrato_com_ia(texto_contrato):
    """
    Recebe o texto de um contrato e usa a IA para analisar e extrair informações chave.
    """
    prompt_analise_contrato = f"""
    Você é um assistente jurídico especializado em contratos da administração pública.
    Sua tarefa é analisar o contrato abaixo e identificar as informações mais relevantes e os possíveis riscos ou pontos de atenção.

    Primeiro, verifique se o texto fornecido parece ser um contrato ou um documento jurídico formal.
    Se não for, devolva o texto: "Não foi possível realizar a análise. O documento fornecido não se trata de um contrato ou não contém informações suficientes para uma análise jurídica. Por favor, envie um contrato válido."
    
    Se o documento for um contrato, divida sua análise EXATAMENTE nas seções a seguir, preenchendo cada uma com a melhor informação possível.

    --- Contrato para Análise ---
    {texto_contrato}
    --- Fim do Contrato ---

    --- Análise do Contrato ---

    **1. RESUMO EXECUTIVO:**
    [Crie um resumo conciso sobre o objeto do contrato, as partes envolvidas e o valor.]

    **2. CLÁUSULAS PRINCIPAIS:**
    [Liste as cláusulas mais importantes do contrato, como objeto, prazos, valor, condições de pagamento e obrigações das partes.]

    **3. PONTOS DE ATENÇÃO E RISCOS:**
    [Identifique possíveis riscos jurídicos, cláusulas ambíguas, prazos apertados, multas excessivas ou qualquer inconsistência que mereça atenção da administração.]

    **4. REFERÊNCIAS LEGAIS:**
    [Mencione as leis ou normas que regem este contrato, como a Lei de Licitações (Lei 14.133/21 ou Lei 8.666/93) ou outras leis aplicáveis.]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_analise_contrato)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com o serviço de IA: {e}"
    
    
def analisar_edital_com_ia(texto_edital):
    """
    Recebe o texto de um edital de licitação e usa a IA para extrair as informações-chave.
    """
    prompt_analise_edital = f"""
    Você é um assistente especializado em licitações públicas. Sua tarefa é analisar o edital a seguir, identificando e extraindo as informações mais relevantes para um gestor público.

    Se o documento fornecido não for um edital ou não contiver informações suficientes, devolva o texto: "Não foi possível realizar a análise. O documento fornecido não parece ser um edital ou não contém informações suficientes para uma análise. Por favor, envie um edital válido."

    Se o documento for um edital, analise-o e devolva as informações EXATAMENTE nas seções a seguir.

    --- Edital para Análise ---
    {texto_edital}
    --- Fim do Edital ---

    --- Análise do Edital ---

    **1. RESUMO GERAL:**
    [Crie um resumo conciso sobre o tipo de licitação (ex: Pregão Eletrônico), o objeto, e a modalidade. Ex: "Pregão Eletrônico para a contratação de serviços de manutenção predial."]

    **2. PONTOS PRINCIPAIS:**
    [Extraia e formate em lista: o **Número do Edital**, **Tipo de Licitação**, **Objeto da Contratação**, **Valor Estimado** e a **Data e Hora da Sessão Pública**.]

    **3. REQUISITOS DE PARTICIPAÇÃO:**
    [Liste os principais requisitos para a participação de empresas na licitação, como exigências de documentos, certidões, ou comprovação de capacidade técnica e financeira.]

    **4. PRAZOS CRONOGRAMA:**
    [Extraia as datas e horários importantes, como: data de entrega das propostas, data da sessão pública, e prazo para recursos.]
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_analise_edital)
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao comunicar com o serviço de IA: {e}"