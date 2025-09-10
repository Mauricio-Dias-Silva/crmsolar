# SysGov_Project/integracao_audesp/services.py

import requests
import json

def enviar_pacote_audesp(json_data, api_key, url_destino):
    """
    Função central para enviar um pacote de dados (JSON) para a API do AUDESP.

    Args:
        json_data (dict): O dicionário Python com os dados a serem enviados.
        api_key (str): A chave de API ou token de autenticação fornecido pelo TCE.
        url_destino (str): A URL do endpoint do TCE (seja de homologação ou produção).

    Returns:
        dict: Um dicionário com o resultado da operação.
              Ex: {'sucesso': True, 'status_code': 200, 'resposta': {'protocolo': '12345'}}
              ou  {'sucesso': False, 'status_code': 400, 'erro': 'CNPJ inválido'}
    """
    # Cabeçalhos da requisição: é aqui que nos autenticamos
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'  # O formato pode variar (ex: 'Token ...'), consulte o manual
    }

    # Converte o nosso dicionário Python para uma string JSON
    data_payload = json.dumps(json_data)

    print(f"--- A ENVIAR PACOTE PARA: {url_destino} ---") # Log para depuração
    print(f"--- PAYLOAD: {data_payload[:200]}... ---")   # Mostra os primeiros 200 caracteres do que estamos a enviar

    try:
        # A chamada à API! O nosso sistema a "conversar" com o TCE.
        response = requests.post(url_destino, data=data_payload, headers=headers, timeout=30)

        # Verifica se a resposta foi bem-sucedida (ex: 200 OK, 201 Created)
        if response.status_code in [200, 201, 202]:
            print("--- RESPOSTA DE SUCESSO DO TCE ---")
            return {
                'sucesso': True,
                'status_code': response.status_code,
                'resposta': response.json()  # A resposta do TCE, geralmente com um número de protocolo
            }
        else:
            # Se deu erro, capturamos a mensagem
            print(f"--- RESPOSTA DE ERRO DO TCE (Status: {response.status_code}) ---")
            return {
                'sucesso': False,
                'status_code': response.status_code,
                'erro': response.text  # A mensagem de erro que o TCE enviou
            }

    except requests.exceptions.RequestException as e:
        # Captura erros de rede (ex: servidor do TCE está offline, sem internet)
        print(f"--- ERRO DE CONEXÃO COM A API: {e} ---")
        return {
            'sucesso': False,
            'status_code': None,
            'erro': f"Erro de comunicação com o servidor do TCE: {e}"
        }
