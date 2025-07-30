# contas/views.py (adicione no final do arquivo)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Notificacao
# Importe o formulário e o modelo Vendedor
from ofertas.forms import CadastroVendedorForm
from ofertas.models import Vendedor # Para verificar se o usuário já é vendedor


@login_required # Apenas usuários logados podem se cadastrar como vendedor
def cadastro_vendedor(request):
    # Verifica se o usuário já está associado a um vendedor
    if request.user.vendedor:
        messages.info(request, 'Você já é um vendedor ou está associado a um.')
        return redirect('vendedores_painel:dashboard') # Redireciona para o painel do vendedor

    if request.method == 'POST':
        form = CadastroVendedorForm(request.POST, request.FILES) # request.FILES para upload de logo
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Cria o novo objeto Vendedor
                    vendedor = form.save(commit=False)
                    vendedor.ativo = True # Ativa por padrão, a aprovação é pelo status
                    vendedor.status_aprovacao = 'pendente' # Define como pendente por padrão
                    vendedor.save()

                    # Vincula o Vendedor recém-criado ao Usuário logado
                    request.user.vendedor = vendedor
                    request.user.save()

                    messages.success(request, 'Seu cadastro de vendedor foi enviado para análise! Em breve entraremos em contato.')
                    return redirect('vendedores_painel:dashboard') # Redireciona para o painel do vendedor
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao processar seu cadastro: {e}')
                # Se for erro de CNPJ duplicado (IntegrityError), a validação do form já deve pegar,
                # mas é bom ter um try/except genérico para outros problemas
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = CadastroVendedorForm()
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Cadastro para Vender no VarejoUnido'
    }
    return render(request, 'contas/cadastro_vendedor.html', contexto)



@login_required
def minhas_notificacoes(request):
    notificacoes = Notificacao.objects.filter(usuario=request.user).order_by('-data_criacao')
    
    # Marcar todas as notificações exibidas como lidas
    Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)

    contexto = {
        'notificacoes': notificacoes,
        'titulo_pagina': 'Minhas Notificações'
    }
    return render(request, 'contas/minhas_notificacoes.html', contexto)