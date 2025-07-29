# pedidos_coletivos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import uuid

from ofertas.models import Oferta
from .models import PedidoColetivo, CreditoUsuario, HistoricoCredito
from compras.models import Cupom 

from django.urls import reverse 

# ... (logger, sdk - existentes) ...

@login_required
def fazer_pedido_coletivo(request, slug_oferta):
    oferta = get_object_or_404(
        Oferta, 
        slug=slug_oferta,
        tipo_oferta='lote', 
        publicada=True,
        status='ativa', 
        data_termino__gte=timezone.now() 
    )

    if not oferta.esta_disponivel_para_compra:
        messages.error(request, 'Esta oferta de compra coletiva não está mais disponível para pedidos.')
        return redirect('ofertas:detalhe_oferta', slug_oferta=oferta.slug)

    # Obtém o saldo de crédito do usuário
    credito_usuario, created = CreditoUsuario.objects.get_or_create(usuario=request.user)
    saldo_disponivel = credito_usuario.saldo

    valor_total_pedido = oferta.preco_desconto # Inicializa com o preço de 1 unidade para o display inicial
    quantidade_comprada = 1 # Quantidade padrão inicial no formulário

    if request.method == 'POST':
        quantidade_comprada = int(request.POST.get('quantidade', 1)) 
        if quantidade_comprada < 1:
            messages.error(request, 'A quantidade deve ser pelo menos 1.')
            return redirect('pedidos_coletivos:fazer_pedido_coletivo', slug_oferta=oferta.slug)

        valor_total_pedido = oferta.preco_desconto * quantidade_comprada # Recalcula com a quantidade do POST
        
        usar_credito = request.POST.get('usar_credito') == 'on'
        valor_a_pagar_mp = valor_total_pedido
        usar_credito_total = False

        if usar_credito and saldo_disponivel > 0:
            if saldo_disponivel >= valor_total_pedido:
                valor_a_pagar_mp = 0.00
                usar_credito_total = True
            else:
                valor_a_pagar_mp = valor_total_pedido - saldo_disponivel
        
        try:
            with transaction.atomic():
                pedido = PedidoColetivo.objects.create(
                    usuario=request.user,
                    oferta=oferta,
                    quantidade=quantidade_comprada,
                    valor_unitario=oferta.preco_desconto,
                    valor_total=valor_total_pedido, 
                    status_pagamento='pendente', 
                    status_lote='aberto' 
                )

                if usar_credito_total:
                    # Se o crédito cobriu tudo, o pedido é aprovado no MP imediatamente
                    credito_usuario.usar_credito(valor_total_pedido, 
                                                 f"Pagamento do Pedido Coletivo '{oferta.titulo}' (Pedido #{pedido.id})")
                    pedido.status_pagamento = 'aprovado_mp'
                    pedido.metodo_pagamento = 'Credito do Site'
                    pedido.save()

                    # Atualiza a quantidade vendida da oferta (para o lote)
                    oferta.quantidade_vendida += pedido.quantidade
                    oferta.save()
                    messages.success(request, f'Seu pedido coletivo para "{oferta.titulo}" foi registrado e pago com seu crédito! Aguarde a concretização do lote.')
                    return redirect('pedidos_coletivos:meus_pedidos')
                else:
                    # Redireciona para o Mercado Pago com o valor restante a pagar
                    messages.info(request, 'Redirecionando para o Mercado Pago para finalizar o pedido coletivo...')
                    request.session['valor_a_cobrar_mp'] = float(valor_a_pagar_mp) # Armazena o valor final na sessão
                    return redirect(reverse('pagamentos:iniciar_pagamento_mp', args=['pedidocoletivo', pedido.id]))

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao preparar seu pedido coletivo: {e}. Por favor, tente novamente.')
            return redirect('ofertas:detalhe_oferta', slug_oferta=oferta.slug)
    
    contexto = {
        'oferta': oferta,
        'saldo_disponivel': saldo_disponivel,
        'valor_unitario_oferta': oferta.preco_desconto, # Passa o valor unitário para cálculo no JS/HTML
        'titulo_pagina': f'Fazer Pedido Coletivo: {oferta.titulo}'
    }
    return render(request, 'pedidos_coletivos/fazer_pedido_coletivo.html', contexto)

# ... (meus_pedidos_coletivos, adicionar_credito_por_lote_falho, verificar_e_processar_lotes_coletivos, meu_credito - mantêm-se) ...

@login_required
def meu_credito(request):
    # Tenta obter o objeto CreditoUsuario do usuário logado
    credito_usuario, created = CreditoUsuario.objects.get_or_create(usuario=request.user)
    historico = HistoricoCredito.objects.filter(credito_usuario=credito_usuario).order_by('-data_transacao')

    contexto = {
        'credito_usuario': credito_usuario,
        'historico': historico,
        'titulo_pagina': 'Meu Crédito no Site'
    }
    return render(request, 'pedidos_coletivos/meu_credito.html', contexto)


@login_required
def meus_pedidos_coletivos(request):
    pedidos = PedidoColetivo.objects.filter(usuario=request.user).order_by('-data_pedido')
    contexto = {
        'pedidos': pedidos,
        'titulo_pagina': 'Meus Pedidos Coletivos'
    }
    return render(request, 'pedidos_coletivos/meus_pedidos_coletivos.html', contexto)

# Função para adicionar crédito no caso de lote não atingido
@transaction.atomic
def adicionar_credito_por_lote_falho(pedido_coletivo):
    # Obtém ou cria o objeto CreditoUsuario para o usuário
    credito_usuario, created = CreditoUsuario.objects.get_or_create(usuario=pedido_coletivo.usuario)
    
    valor_a_adicionar = pedido_coletivo.valor_total
    descricao_credito = f"Crédito por falha no lote da oferta: '{pedido_coletivo.oferta.titulo}' (Pedido #{pedido_coletivo.id})"
    
    credito_usuario.adicionar_credito(valor_a_adicionar, descricao_credito)
    
    # Atualiza o status do pedido para indicar que foi processado o reembolso em crédito
    pedido_coletivo.status_lote = 'falha' # Altera o status do lote para falha
    pedido_coletivo.status_pagamento = 'lote_cancelado_com_credito' # Novo status para controle
    pedido_coletivo.save()
    
    messages.info(pedido_coletivo.usuario, f'O lote da oferta "{pedido_coletivo.oferta.titulo}" não foi concretizado. O valor de R$ {valor_a_adicionar:.2f} foi adicionado como crédito em sua conta.')
    # Não pode usar messages diretamente aqui se chamado de Celery task, mas pode ser um e-mail.
    logger.info(f"Crédito de R${valor_a_adicionar:.2f} adicionado ao usuário {pedido_coletivo.usuario.username} por falha de lote do pedido {pedido_coletivo.id}.")


# Tarefa Celery para verificar e processar lotes no novo app pedidos_coletivos
from celery import shared_task
import logging

logger_tasks = logging.getLogger('pedidos_coletivos.tasks') # Um logger diferente para tarefas

@shared_task
def verificar_e_processar_lotes_coletivos():
    logger_tasks.info("Iniciando verificação e processamento de pedidos coletivos...")
    
    # Busca ofertas do tipo 'lote' que expiraram e ainda estão 'ativas' ou 'pendente' (aguardando processamento)
    ofertas_lote_expiradas = Oferta.objects.filter(
        tipo_oferta='lote',
        status__in=['ativa', 'pendente'], # Ofertas que ainda não foram marcadas como sucesso/falha_lote
        data_termino__lt=timezone.now() # A data de término é no passado
    ).distinct() # Para evitar duplicidade

    for oferta in ofertas_lote_expiradas:
        with transaction.atomic():
            oferta.refresh_from_db() # Garante que estamos com a versão mais recente
            logger_tasks.info(f"Processando oferta de lote '{oferta.titulo}' (ID: {oferta.id}) - Qtd Vendida: {oferta.quantidade_vendida}, Mínimo: {oferta.quantidade_minima_ativacao}")

            if oferta.quantidade_vendida >= oferta.quantidade_minima_ativacao:
                # Lote BEM-SUCEDIDO
                oferta.status = 'sucesso'
                oferta.save()
                logger_tasks.info(f"Oferta '{oferta.titulo}' - Lote CONCRETIZADO! Processando pedidos aprovados.")
                
                pedidos_aprovados = PedidoColetivo.objects.filter(
                    oferta=oferta, 
                    status_pagamento='aprovado_mp', # Pagamento aprovado no MP
                    status_lote='aberto' # Ainda esperando concretização
                )
                
                for pedido in pedidos_aprovados:
                    try:
                        pedido.status_lote = 'concretizado'
                        pedido.data_cupom_gerado = timezone.now()
                        pedido.cupom_gerado = str(uuid.uuid4()).replace('-', '')[:12].upper() # Gera o código do cupom
                        pedido.save()

                        # Crie o cupom no app 'compras' para este pedido
                        Cupom.objects.create(
                            compra=None, # Este cupom não tem uma 'Compra' direta, mas sim um PedidoColetivo
                            oferta=oferta,
                            usuario=pedido.usuario,
                            codigo=pedido.cupom_gerado,
                            valido_ate=oferta.data_termino,
                            status='disponivel'
                        )
                        logger_tasks.info(f"Pedido Coletivo {pedido.id}: Lote concretizado, cupom {pedido.cupom_gerado} gerado.")

                    except Exception as e:
                        logger_tasks.error(f"Erro ao processar pedido coletivo {pedido.id} (sucesso): {e}", exc_info=True)
            else:
                # Lote FALHOU
                oferta.status = 'falha_lote'
                oferta.save()
                logger_tasks.warning(f"Oferta '{oferta.titulo}' - Lote FALHOU! ({oferta.quantidade_vendida}/{oferta.quantidade_minima_ativacao}). Reembolsando/Creditando.")
                
                pedidos_falhos = PedidoColetivo.objects.filter(
                    oferta=oferta, 
                    status_pagamento='aprovado_mp', # Pagamento aprovado no MP, mas lote falhou
                    status_lote='aberto' # Ainda esperando concretização
                )
                
                for pedido in pedidos_falhos:
                    try:
                        # Chamar a função para adicionar crédito
                        adicionar_credito_por_lote_falho(pedido)
                        logger_tasks.info(f"Pedido Coletivo {pedido.id}: Lote falhou, valor creditado ao usuário.")

                    except Exception as e:
                        logger_tasks.error(f"Erro ao processar reembolso (crédito) para pedido coletivo {pedido.id} (falha): {e}", exc_info=True)
    
    logger_tasks.info("Verificação e processamento de pedidos coletivos concluído.")