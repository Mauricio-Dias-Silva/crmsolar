# integracao_audesp/client.py

import requests
import json
from django.conf import settings
from django.core.cache import cache
from .exceptions import AudespAPIError, AudespAuthenticationError

class AudespClient:
    def __init__(self):
        # Pega as configurações do settings.py (lembre-se de adicioná-las lá!)
        self.base_url = settings.AUDESP_API_BASE_URL
        self.email = settings.AUDESP_API_EMAIL
        self.password = settings.AUDESP_API_PASSWORD

    def _get_token(self):
        """Pega o token do cache ou solicita um novo se não existir/expirou."""
        token = cache.get('audesp_api_token')
        if token:
            return token

        login_url = f"{self.base_url}/login"
        auth_string = f"{self.email}:{self.password}"
        headers = {'x-authorization': auth_string, 'User-Agent': 'SysGov-Project/1.0'}

        try:
            response = requests.post(login_url, headers=headers, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get('token') or token_data.get('access_token')
                # A documentação não diz o tempo, vamos assumir 1h (3600s)
                # Cache por 55 minutos para ter margem de segurança
                cache.set('audesp_api_token', token, timeout=3300)
                return token
            elif response.status_code in [401, 403]:
                raise AudespAuthenticationError("Falha na autenticação. Verifique as credenciais ou permissões.", response.status_code)
            else:
                raise AudespAPIError("Erro inesperado ao obter token.", response.status_code, response.text)
        except requests.exceptions.RequestException as e:
            raise AudespAPIError(f"Erro de conexão ao obter token: {e}")

    def enviar_edital(self, dados_edital_json: dict, caminho_arquivo_pdf: str):
        """
        Envia um edital para a API da Audesp.
        Recebe um dicionário com os dados e o caminho para o arquivo PDF.
        """
        token = self._get_token()
        envio_url = f"{self.base_url}/f4/enviar-edital"
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'SysGov-Project/1.0'
        }

        try:
            with open(caminho_arquivo_pdf, 'rb') as arquivo_pdf:
                files = {
                    'documentoJSON': (None, json.dumps(dados_edital_json), 'application/json'),
                    'arquivoPDF': (caminho_arquivo_pdf.split('/')[-1], arquivo_pdf, 'application/pdf')
                }
                
                response = requests.post(envio_url, headers=headers, files=files, timeout=30)

                if response.status_code == 200:
                    return response.json() # Sucesso! Retorna {'protocolo': '...', 'mensagem': '...'}
                else:
                    # Lança um erro com detalhes para a view poder tratar
                    raise AudespAPIError(
                        "A API da Audesp retornou um erro.",
                        status_code=response.status_code,
                        response_text=response.text
                    )
        except FileNotFoundError:
            raise AudespAPIError(f"Arquivo PDF não encontrado no caminho: {caminho_arquivo_pdf}")
        except requests.exceptions.RequestException as e:
            raise AudespAPIError(f"Erro de conexão ao enviar o edital: {e}")