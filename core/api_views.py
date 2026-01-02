# SysGov_Project/core/views.py (ou um novo core/api_views.py)

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse # Se você quiser mais tarde retornar JSON

# Importe os modelos necessários dos outros apps (ex: Edital, ETP, TR, DocumentoFiscal, Pagamento)
from contratacoes.models import ETP, TR
from licitacoes.models import Edital
from financeiro.models import DocumentoFiscal, Pagamento


@login_required
def render_etp_detail_snippet(request, pk):
    etp = get_object_or_404(ETP, pk=pk)
    # Adicione verificação de permissão:
    if etp.processo_vinculado and etp.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este ETP.", status=403)

    html_content = render_to_string('core/snippets/etp_detail_snippet.html', {'etp': etp, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_tr_detail_snippet(request, pk):
    tr = get_object_or_404(TR, pk=pk)
    if tr.processo_vinculado and tr.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este TR.", status=403)
    html_content = render_to_string('core/snippets/tr_detail_snippet.html', {'tr': tr, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_edital_detail_snippet(request, pk):
    edital = get_object_or_404(Edital, pk=pk)
    if edital.processo_vinculado and edital.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Edital.", status=403)
    html_content = render_to_string('core/snippets/edital_detail_snippet.html', {'edital': edital, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_df_detail_snippet(request, pk):
    df = get_object_or_404(DocumentoFiscal, pk=pk)
    if df.processo_vinculado and df.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Documento Fiscal.", status=403)
    html_content = render_to_string('core/snippets/df_detail_snippet.html', {'df': df, 'request': request})
    return HttpResponse(html_content)

@login_required
def render_pagamento_detail_snippet(request, pk):
    pg = get_object_or_404(Pagamento, pk=pk)
    if pg.processo_vinculado and pg.processo_vinculado.usuario != request.user:
        return HttpResponse("Você não tem permissão para visualizar este Pagamento.", status=403)
    html_content = render_to_string('core/snippets/pagamento_detail_snippet.html', {'pagamento': pg, 'request': request})
    return HttpResponse(html_content)