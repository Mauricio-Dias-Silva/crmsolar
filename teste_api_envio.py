import requests
import json

# --- Seus dados (os mesmos que funcionaram) ---
email = "suprimentos.mauriciodias@barueri.sp.gov.br" # O e-mail que você usa no portal
senha = "M@ur1c1001"
api_base_url = "https://audesp-piloto.tce.sp.gov.br"

def obter_token():
    # Esta função é a mesma, já sabemos que funciona
    login_url = f"{api_base_url}/login"
    auth_string = f"{email}:{senha}"
    headers = {'x-authorization': auth_string, 'User-Agent': 'SysGov-Project-Test-Client/1.0'}
    try:
        response = requests.post(login_url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('token') or token_data.get('access_token')
        return None
    except requests.exceptions.RequestException:
        return None

def enviar_edital_teste(token):
    """Função para montar e enviar um edital de teste."""
    if not token:
        print("Não foi possível enviar, pois não temos um token.")
        return

    # --- ETAPA 1: Montar o JSON com dados de teste ---
    # Pegamos os campos obrigatórios da documentação para um edital simples.
    # OBS: Estes valores são apenas para teste, podem precisar de ajustes.
    dados_edital_json = {
        "descritor": {
            "municipio": 3510609,  # Código IBGE de Carapicuíba, por exemplo
            "entidade": 1,         # ID da entidade, 1 é um valor comum de teste
            "ano": 2025,
            "codigoEdital": "SYSGOV-TESTE-001",
            "dataPublicacao": "2025-10-17",
            "retificacao": False
        },
        "codigoUnidadeCompradora": "UC-TESTE-01",
        "tipoInstrumentoConvocatorioId": 1,
        "modalidadeId": 9, # Pregão
        "modoDisputaId": 1, # Aberto
        "numeroCompra": "123/2025",
        "anoCompra": 2025,
        "numeroProcesso": "PROC-987/2025",
        "objetoCompra": "Objeto de teste para aquisicao de materiais via API SysGov",
        "srp": False,
        "dataAberturaProposta": "2025-11-01T10:00:00",
        "dataEncerramentoProposta": "2025-11-10T17:00:00",
        "itensCompra": [
            {
                "numeroItem": 1,
                "materialOuServico": "M",
                "tipoBeneficioId": 1,
                "incentivoProdutivoBasico": False,
                "descricao": "Item de teste 1 - Caneta esferografica",
                "quantidade": 100.0,
                "unidadeMedida": "UN",
                "orcamentoSigiloso": False,
                "valorUnitarioEstimado": 1.50,
                "valorTotal": 150.00,
                "criterioJulgamentoId": 1,
                "itemCategoriaId": 3
            }
        ]
    }

    # --- ETAPA 2: Preparar a requisição ---
    envio_url = f"{api_base_url}/f4/enviar-edital"
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'SysGov-Project-Test-Client/1.0'
    }

    # O 'requests' lida com multipart/form-data de forma inteligente
    # Precisamos de um arquivo PDF de exemplo na mesma pasta do script
    nome_arquivo_pdf = 'edital_teste.pdf'

    print(f"\n--- ETAPA 3: Tentando enviar o edital de teste ({nome_arquivo_pdf}) ---")

    try:
        with open(nome_arquivo_pdf, 'rb') as arquivo_pdf:
            # Montamos o payload com as duas partes: o JSON e o arquivo
            files = {
                'documentoJSON': (None, json.dumps(dados_edital_json), 'application/json'),
                'arquivoPDF': (nome_arquivo_pdf, arquivo_pdf, 'application/pdf')
            }
            
            response = requests.post(envio_url, headers=headers, files=files)

            # --- ETAPA 4: Analisando a resposta do envio ---
            print(f"Status da Resposta do Envio: {response.status_code}")
            try:
                print("Resposta do servidor (JSON):", response.json())
            except json.JSONDecodeError:
                print("Resposta do servidor (não é JSON):", response.text)

    except FileNotFoundError:
        print(f"\nERRO: Arquivo '{nome_arquivo_pdf}' não encontrado!")
        print("Por favor, crie um arquivo PDF de exemplo com este nome na mesma pasta do script.")
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão no envio: {e}")

# --- Execução Principal ---
if __name__ == "__main__":
    meu_token = obter_token()
    if meu_token:
        print("Token obtido com sucesso.")
        enviar_edital_teste(meu_token)