# integracao_audesp/mappers.py

import json
from licitacoes.models import Edital

def formatar_edital_para_audesp(edital_obj: Edital):
    """
    Recebe um objeto Edital do nosso banco de dados e retorna um dicionário
    pronto para ser convertido em JSON e enviado para a API da Audesp.
    """

    dados_formatados = {
        "descritor": {
            "municipio": 3510609,
            "entidade": 1,
            "ano": edital_obj.ano_compra_audesp or edital_obj.data_publicacao.year,
            "codigoEdital": f"SYSGOV-{edital_obj.id}",
            "dataPublicacao": edital_obj.data_publicacao.strftime('%Y-%m-%d'),
            "retificacao": edital_obj.retificacao
        },
        "codigoUnidadeCompradora": edital_obj.codigo_unidade_compradora,
        "tipoInstrumentoConvocatorioId": edital_obj.tipo_instrumento_convocatorio_audesp,
        "modalidadeId": edital_obj.modalidade_audesp,
        "modoDisputaId": edital_obj.modo_disputa,
        "numeroCompra": edital_obj.numero_compra_audesp,
        "anoCompra": edital_obj.ano_compra_audesp,
        "numeroProcesso": edital_obj.numero_processo_origem_audesp,
        "objetoCompra": edital_obj.objeto_compra_audesp,
        "informacaoComplementar": edital_obj.informacao_complementar,
        "srp": edital_obj.srp,
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Verifica se as datas existem antes de tentar formatá-las
        "dataAberturaProposta": edital_obj.data_abertura_propostas.strftime('%Y-%m-%dT%H:%M:%S') if edital_obj.data_abertura_propostas else None,
        "dataEncerramentoProposta": edital_obj.data_encerramento_proposta.strftime('%Y-%m-%dT%H:%M:%S') if edital_obj.data_encerramento_proposta else None,
        
        "amparoLegalId": edital_obj.amparo_legal,
        "linkSistemaOrigem": edital_obj.link_sistema_origem,
        "justificativaPresencial": edital_obj.justificativa_presencial,

        "itensCompra": [
            {
                "numeroItem": item.numero_item_audesp,
                "materialOuServico": item.material_ou_servico,
                "tipoBeneficioId": item.tipo_beneficio,
                "incentivoProdutivoBasico": item.incentivo_produtivo_basico,
                "descricao": item.descricao_item,
                "quantidade": float(item.quantidade) if item.quantidade is not None else 0.0,
                "unidadeMedida": item.unidade_medida,
                "orcamentoSigiloso": item.orcamento_sigiloso,
                "valorUnitarioEstimado": float(item.valor_unitario_estimado_audesp) if item.valor_unitario_estimado_audesp is not None else 0.0,
                "valorTotal": float(item.valor_total_audesp) if item.valor_total_audesp is not None else 0.0,
                "criterioJulgamentoId": item.criterio_julgamento,
                "itemCategoriaId": item.item_categoria,
                "patrimonio": item.patrimonio,
                "codigoRegistroImobiliario": item.codigo_registro_imobiliario
            }
            for item in edital_obj.itens_diretos.all()
        ]
    }

    # Remove chaves com valores None, pois a API pode não aceitá-las
    dados_limpos = {k: v for k, v in dados_formatados.items() if v is not None}
    
    # A seção 'itensCompra' também precisa ter seus itens limpos de valores None
    if 'itensCompra' in dados_limpos:
        dados_limpos['itensCompra'] = [
            {k_item: v_item for k_item, v_item in item.items() if v_item is not None}
            for item in dados_limpos['itensCompra']
        ]

    return dados_limpos