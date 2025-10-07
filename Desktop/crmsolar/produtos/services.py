
        
import json
import re
from django.conf import settings
import google.generativeai as genai

# Configuração da API do Gemini (deixe como está)
try:
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    else:
        print("AVISO: Chave da API do Gemini não encontrada.")
except Exception as e:
    print(f"ERRO ao configurar a API do Gemini: {e}")


# SUBSTITUA A FUNÇÃO INTEIRA POR ESTA VERSÃO CORRIGIDA:
def analisar_imagem_produto(imagem_ia):
    """
    Esta função usa a API real do Google Gemini para analisar a imagem.
    """
    if not settings.GEMINI_API_KEY:
        return {'error': 'A chave da API do Gemini não foi configurada no servidor.'}

    # A estrutura try...except começa aqui
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash-image-preview')

        imagem_bytes = imagem_ia.read()
        imagem_parts = [{"mime_type": imagem_ia.content_type, "data": imagem_bytes}]

        prompt = """
        Você é um especialista em catalogar produtos de energia solar.
        Analise a imagem deste produto e me retorne APENAS um objeto JSON com as seguintes chaves:
        - "name": O nome comercial completo e técnico do produto.
        - "description": Uma descrição curta e objetiva do produto.
        - "preco": Um preço de venda estimado em BRL, como uma string (ex: "1250.75").
        - "categoria_id": Uma das seguintes opções: 'paineis_solares', 'inversores', 'baterias', 'kits_fotovoltaicos', 'estruturas_montagem', 'acessorios', 'outros'.
        - "sku": Um código SKU sugerido.
        - "peso": O peso estimado em kg, como uma string (ex: "22.5").
        - "dimensoes": As dimensões estimadas em cm (ex: "175cm x 110cm x 4cm").
        - "garantia": O tempo de garantia comum (ex: "12 anos").
        - "stock": Um valor de estoque inicial sugerido (ex: 20).
        - "is_active": Sempre retorne true.
        Se não conseguir identificar, retorne um JSON com "name" como "Produto Não Identificado".
        NÃO inclua nenhuma formatação de markdown (como ```json) na sua resposta.
        """

        print("Enviando imagem para a API do Gemini...")
        response = model.generate_content([prompt, *imagem_parts])
        print("Resposta recebida da IA.")
        
        json_str = response.text
        dados_encontrados = json.loads(json_str)
        
        print("Dados extraídos com sucesso:", dados_encontrados)
        return dados_encontrados

    # O bloco 'except' obrigatório vem logo após o 'try'
    except Exception as e:
        print(f"ERRO CRÍTICO ao chamar a API do Gemini: {e}")
        return {'error': f'Falha na comunicação com a IA: {e}'}