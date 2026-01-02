# integracao_audesp/utils.py (ou onde faz sentido para suas validações)
import json
import os
from jsonschema import validate, ValidationError

# Caminho base para seus schemas (ajuste conforme a estrutura do seu projeto)
SCHEMA_BASE_PATH = os.path.join(os.path.dirname(__file__), 'schemas')

def validate_json_with_schema(json_data, schema_name):
    """
    Valida um dicionário Python (JSON) contra um schema JSON específico do AUDESP.

    Args:
        json_data (dict): O dicionário Python que representa o JSON a ser validado.
        schema_name (str): O nome do arquivo do schema (ex: 'audesp_edital_v4.json').

    Returns:
        bool: True se o JSON for válido, False caso contrário.
        list: Lista de erros de validação, se houver.
    """
    schema_path = os.path.join(SCHEMA_BASE_PATH, schema_name)

    if not os.path.exists(schema_path):
        return False, [f"Schema '{schema_name}' não encontrado em {SCHEMA_BASE_PATH}"]

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    try:
        validate(instance=json_data, schema=schema)
        return True, []
    except ValidationError as e:
        errors = []
        for error in sorted(e.errors, key=str): # Coleta todos os erros, se houver
            errors.append(f"Erro de Validação: {error.message} (Caminho: {error.path}, Schema: {error.schema_path})")
        return False, errors
    except Exception as e:
        return False, [f"Erro inesperado durante a validação: {str(e)}"]