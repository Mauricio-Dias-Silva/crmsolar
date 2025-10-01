# populate.py
import os
import django
from django.utils import timezone
from django.contrib.auth import get_user_model
# Se você tiver o Faker instalado e quiser dados mais realistas:
# from faker import Faker
# import random

# --- IMPORTANTE: Configure o ambiente Django ---
# Substitua 'crmsolar' pelo nome real da sua pasta principal do Django que contém o settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crmsolar.settings')
django.setup()

# --- IMPORTANTE: Importe seus modelos aqui ---
# Exemplo:
# from meu_app.models import Categoria, Produto, Cliente, Pedido, Projeto, Fornecedor, Material, LancamentoFinanceiro, RegiaoFrete
# from crm.models import Cliente, Projeto, Fornecedor, Material
# from ecommerce.models import Produto, Pedido, RegiaoFrete
# from core.models import UsuarioPersonalizado # Se você tiver um User model customizado

User = get_user_model()
# faker = Faker('pt_BR') # Descomente se for usar Faker

def populate_data():
    """
    Função principal para popular o banco de dados com dados fictícios.
    """
    print("Iniciando população de dados...")
    print("-" * 30)

    # --- 1. Criar um superusuário (se não existir) ---
    try:
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin') # Senha 'admin'
            print(f"✅ Superusuário 'admin' criado: {admin_user.username}")
        else:
            print("ℹ️ Superusuário 'admin' já existe.")
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
    print("-" * 30)

    # --- 2. Exemplo: População de um modelo de 'Cliente' (Adapte para seus modelos!) ---
    # Substitua 'Cliente' e os campos pelos seus modelos reais
    # Descomente e adapte o bloco abaixo se você tiver um modelo de Cliente
    # try:
    #     if Cliente.objects.exists():
    #         print("🗑️ Limpando dados antigos de Clientes...")
    #         Cliente.objects.all().delete()

    #     print("Criando 10 clientes de exemplo...")
    #     for i in range(1, 11):
    #         cliente = Cliente.objects.create(
    #             nome=faker.name(),
    #             email=faker.email(),
    #             telefone=faker.phone_number(),
    #             endereco=faker.address(),
    #             data_cadastro=timezone.now()
    #         )
    #         print(f"  - Cliente criado: {cliente.nome}")
    #     print(f"✅ {Cliente.objects.count()} Clientes criados.")
    # except NameError:
    #     print("⚠️ Modelo 'Cliente' não importado ou não existe. Pulando população de Clientes.")
    # except Exception as e:
    #     print(f"❌ Erro ao popular Clientes: {e}")
    # print("-" * 30)


    # --- 3. Exemplo: População de um modelo de 'Projeto' (Adapte para seus modelos!) ---
    # Se você tem um modelo de Projeto e ele se relaciona com Cliente, use algo assim:
    # Descomente e adapte o bloco abaixo
    # try:
    #     if Projeto.objects.exists():
    #         print("🗑️ Limpando dados antigos de Projetos...")
    #         Projeto.objects.all().delete()

    #     print("Criando projetos de exemplo...")
    #     clientes_existentes = Cliente.objects.all()
    #     if clientes_existentes.exists():
    #         status_choices = ['Pendente', 'Em Andamento', 'Concluído', 'Cancelado']
    #         for i in range(1, 15): # Criar 15 projetos
    #             projeto = Projeto.objects.create(
    #                 cliente=random.choice(clientes_existentes),
    #                 titulo=f"Instalação Solar {faker.city()}",
    #                 descricao=faker.paragraph(nb_sentences=2),
    #                 valor_estimado=round(random.uniform(10000.00, 100000.00), 2),
    #                 data_inicio=timezone.now() - timezone.timedelta(days=random.randint(10, 365)),
    #                 data_conclusao=timezone.now() + timezone.timedelta(days=random.randint(30, 180)) if random.random() > 0.3 else None,
    #                 status=random.choice(status_choices)
    #             )
    #             print(f"  - Projeto criado: {projeto.titulo} para {projeto.cliente.nome}")
    #         print(f"✅ {Projeto.objects.count()} Projetos criados.")
    #     else:
    #         print("ℹ️ Nenhum cliente encontrado para vincular projetos. Crie clientes primeiro.")
    # except NameError:
    #     print("⚠️ Modelo 'Projeto' ou 'Cliente' não importado ou não existe. Pulando população de Projetos.")
    # except Exception as e:
    #     print(f"❌ Erro ao popular Projetos: {e}")
    # print("-" * 30)

    # --- Adicione aqui a lógica para popular outros modelos (Produto, Pedido, etc.) ---
    # Use a mesma estrutura try/except e adapte para os campos e relacionamentos dos seus modelos.
    # Exemplo para outro modelo:
    # try:
    #     if Produto.objects.exists():
    #         print("🗑️ Limpando dados antigos de Produtos...")
    #         Produto.objects.all().delete()
    #     print("Criando produtos de exemplo...")
    #     for i in range(5):
    #         Produto.objects.create(
    #             nome=f"Produto {i+1} - {faker.word().capitalize()}",
    #             preco=random.uniform(50.00, 500.00),
    #             estoque=random.randint(10, 100)
    #         )
    #     print(f"✅ {Produto.objects.count()} Produtos criados.")
    # except NameError:
    #     print("⚠️ Modelo 'Produto' não importado ou não existe. Pulando população de Produtos.")
    # except Exception as e:
    #     print(f"❌ Erro ao popular Produtos: {e}")
    # print("-" * 30)


    print("\nPopulação de dados concluída!")
    print("Verifique seu painel de administração e o site para ver os novos dados. ✨")

if __name__ == '__main__':
    # Esta linha executa a função populate_data quando o script é chamado diretamente.
    populate_data()