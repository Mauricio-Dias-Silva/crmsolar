import requests
import base64 # A documentação é um pouco ambígua, mas geralmente isso é enviado em base64

# --- Seus dados ---
email = "suprimentos.mauriciodias@barueri.sp.gov.br" # O e-mail que você usa no portal
senha = "M@ur1c1001"
api_base_url = "https://audesp-piloto.tce.sp.gov.br"

# --- A Requisição ---
login_url = f"{api_base_url}/login"

# A API pede "email:senha" no header. Vamos criar isso.
auth_string = f"{email}:{senha}"

headers = {
    'x-authorization': auth_string
}

print(f"Tentando autenticar em: {login_url}")

try:
    response = requests.post(login_url, headers=headers)

    # --- Análise do Resultado ---
    print(f"Status da Resposta: {response.status_code}")
    
    if response.status_code == 200:
        print("Autenticação BEM-SUCEDIDA!")
        token_data = response.json()
        print("Token recebido:", token_data)
        # AQUI GUARDARÍAMOS O TOKEN PARA OS PRÓXIMOS PASSOS
    else:
        print("FALHA na autenticação.")
        print("Resposta do servidor:", response.json())

except requests.exceptions.RequestException as e:
    print(f"Erro de conexão: {e}")