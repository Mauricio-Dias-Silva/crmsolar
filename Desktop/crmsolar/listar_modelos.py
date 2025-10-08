import os
import requests
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente (o arquivo .env)
load_dotenv()

# Pega a chave da API
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: A variável GEMINI_API_KEY não foi encontrada no arquivo .env")
else:
    # URL do endpoint da API do Google para listar modelos
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    print("Conectando diretamente com a API do Google...")

    try:
        # Faz a requisição web, como se fosse um navegador
        response = requests.get(url)

        # Verifica se a requisição foi bem-sucedida (código 200)
        response.raise_for_status()

        # Pega a resposta em formato JSON
        data = response.json()
        models = data.get('models', [])

        print("\n--- Modelos Disponíveis para Geração de Conteúdo ---")
        if not models:
            print("Nenhum modelo encontrado. Verifique se sua chave de API está correta e ativada.")
        else:
            for model in models:
                # Filtra e mostra apenas os modelos que podem gerar texto
                if 'generateContent' in model.get('supportedGenerationMethods', []):
                    print(f"- {model.get('name')}")

        print("\nCopie um dos nomes acima (ex: 'models/gemini-1.5-flash-latest') e cole no seu arquivo services.py")

    except requests.exceptions.HTTPError as e:
        print(f"\nERRO HTTP: {e.response.status_code} - {e.response.text}")
        print("Isso geralmente significa que a chave da API é inválida ou não tem permissão.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado ao conectar com a API: {e}")
