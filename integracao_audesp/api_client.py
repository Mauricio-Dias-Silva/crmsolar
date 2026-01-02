# integracao_audesp/api_client.py
import requests
import json

# URL base do seu mock da API do AUDESP
MOCK_API_BASE_URL = "http://localhost:8000/mock-audesp/" # Verifique a porta do seu runserver

def get_mock_audesp_token(email, password):
    """Simula a obtenção de um token de autenticação do mock da API."""
    url = f"{MOCK_API_BASE_URL}login/"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({'email': email, 'password': password})

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status() # Lança um erro para status 4xx/5xx
        return response
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token do mock: {e}")
        return None

def enviar_json_para_mock_audesp(json_payload, schema_type, token):
    """
    Simula o envio de um pacote JSON para o mock da API do AUDESP.

    Args:
        json_payload (str): O JSON como string.
        schema_type (str): O tipo de esquema (ex: 'edital-detalhado', 'ajuste-contratual').
        token (str): O token de autenticação obtido do mock login.
    """
    url = f"{MOCK_API_BASE_URL}enviar/{schema_type}/"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.post(url, headers=headers, data=json_payload)
        response.raise_for_status() # Lança um erro para status 4xx/5xx
        print(f"Resposta do mock ({schema_type}): Status {response.status_code}, {response.json()}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar JSON para o mock ({schema_type}): {e}")
        # Tenta retornar a resposta mesmo em caso de erro para ver o detalhe
        if hasattr(e, 'response') and e.response is not None:
            return e.response
        return None
    

