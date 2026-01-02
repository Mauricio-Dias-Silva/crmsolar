# integracao_audesp/exceptions.py
class AudespAPIError(Exception):
    """Erro genérico de comunicação com a API Audesp."""
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class AudespAuthenticationError(AudespAPIError):
    """Erro específico de autenticação."""
    pass