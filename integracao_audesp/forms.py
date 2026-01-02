# SysGov_Project/integracao_audesp/forms.py

from django import forms
from .models import AudespConfiguracao, SubmissaoAudesp

# Formulário para o modelo de Configuração (útil para o Admin)
class AudespConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = AudespConfiguracao
        fields = '__all__'

# Formulário para o modelo de Submissão (útil para o Admin)
class SubmissaoAudespForm(forms.ModelForm):
    class Meta:
        model = SubmissaoAudesp
        fields = '__all__'
