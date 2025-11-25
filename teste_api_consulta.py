import requests
import json # Importamos a biblioteca json para o tratamento de erro

# --- Seus dados (os mesmos que funcionaram) ---
email = "suprimentos.mauriciodias@barueri.sp.gov.br" # O e-mail que você usa no portal
senha = "M@ur1c1001"
api_base_url = "https://audesp-piloto.tce.sp.gov.br"

def obter_token():
    """Função para autenticar e obter o token de acesso."""
    login_url = f"{api_base_url}/login"
    auth_string = f"{email}:{senha}"
    headers = {
        'x-authorization': auth_string,
        'User-Agent': 'SysGov-Project-Test-Client/1.0',
        'Content-Type': 'application/json'
    }

    print("--- ETAPA 1: Autenticando para obter o token ---")
    try:
        response = requests.post(login_url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('token') or token_data.get('access_token')
            print("Autenticação BEM-SUCEDIDA!")
            return token
        else:
            print(f"FALHA na autenticação. Status: {response.status_code}")
            print("Resposta:", response.text) # Usamos .text para garantir que não quebre
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão na autenticação: {e}")
        return None

def consultar_protocolo(token):
    """Função para consultar um protocolo usando o token."""
    if not token:
        print("Não foi possível consultar, pois não temos um token.")
        return

    protocolo_exemplo = 'FFABC71071004801'
    consulta_url = f"{api_base_url}/consulta/{protocolo_exemplo}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'SysGov-Project-Test-Client/1.0'
    }

    print(f"\n--- ETAPA 2: Consultando o protocolo {protocolo_exemplo} ---")
    try:
        response = requests.get(consulta_url, headers=headers)
        
        print(f"Status da Resposta da Consulta: {response.status_code}")

        # Agora vamos tentar ler a resposta de forma segura
        try:
            # Tenta decodificar a resposta como JSON
            resposta_servidor = response.json()
            print("Resposta do servidor (JSON):", resposta_servidor)
        except json.JSONDecodeError:
            # Se falhar, significa que não era JSON, então imprime como texto
            print("Resposta do servidor (não é JSON):", response.text)

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão na consulta: {e}")


# --- Execução Principal do Script ---
if __name__ == "__main__":
    meu_token = obter_token()
    
    if meu_token:
        consultar_protocolo(meu_token)