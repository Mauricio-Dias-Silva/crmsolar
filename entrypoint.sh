#!/bin/bash
# entrypoint.sh - Script de inicialização para o Cloud Run

# Sair imediatamente se um comando falhar
set -e

echo "Iniciando script de entrypoint..."

# 1. Coletar arquivos estáticos (resolve o CSS do Admin)
echo "1. Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# 2. Executar migrações do banco de dados
echo "2. Executando migrações do banco de dados..."
# Usamos o comando 'migrate' aqui. Se a aplicação não puder se conectar ao
# Cloud SQL imediatamente, você pode adicionar um loop de espera usando nc (netcat)
# ou a ferramenta 'wait-for-it', mas para o Cloud Run geralmente a migração funciona
# se o Cloud SQL estiver configurado corretamente.
python manage.py migrate --no-input

# 3. Iniciar o servidor Gunicorn
echo "3. Iniciando servidor Gunicorn..."
# O Gunicorn precisa escutar a porta definida pelo Cloud Run (padrão é 8080)
# energia_solar é o nome do seu projeto Django.
gunicorn energia_solar.wsgi:application --bind 0.0.0.0:$PORT
