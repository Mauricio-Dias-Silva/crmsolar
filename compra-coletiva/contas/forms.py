# contas/forms.py
from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    # Exemplo: campo extra (opcional)
    nome_completo = forms.CharField(max_length=100, label='Nome completo')

    def save(self, request):
        user = super().save(request)
        # Se quiser salvar o nome, por exemplo:
        user.nome_completo = self.cleaned_data['nome_completo']
        user.save()
        return user
    
