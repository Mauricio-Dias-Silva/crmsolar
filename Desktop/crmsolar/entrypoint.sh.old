#!/bin/sh

echo "Aguardando o MySQL iniciar..."
# 'nc -z' verifica se a porta 3306 do serviço 'db' está aberta
# Se não estiver, o loop continua e o script espera por 2 segundos
while ! nc -z db 3306; do
  sleep 2
done
echo "MySQL iniciado!"

# Garante que o diretório de trabalho está certo
cd /app

# Aplica as migrações existentes. É o comando correto para ambientes de produção.
echo "Aplicando migrações..."
python manage.py migrate --noinput

# Executa o seu script de populamento de dados
# Este script deve conter a lógica para criar todos os usuários de teste,
# incluindo o superusuário.
echo "Executando script de populamento de dados..."
python manage.py populate_usuarios_e_departamentos
python manage.py populate_clientes_pf
python manage.py populate_clientes_pj
python manage.py populate_produtos
python manage.py populate_fornecedores
python manage.py populate_materiais
python manage.py populate_projetos_pedidos


echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Inicia o servidor Django. O 'exec' garante que o servidor
# se torne o processo principal do contêiner.
echo "Iniciando o servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
# O comando 'exec' substitui o shell atual pelo comando especificado,
