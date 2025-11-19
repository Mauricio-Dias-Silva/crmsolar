#!/bin/bash
# entrypoint.sh - Script de inicialização para o Cloud Run

# Sair imediatamente se um comando falhar
set -e

echo "Iniciando script de entrypoint..."

# 1. Coletar arquivos estáticos
echo "1. Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# 2. Executar migrações
# O Django tentará conectar no socket definido no settings.py
echo "2. Executando migrações do banco de dados..."
python manage.py migrate --no-input

# 3. Iniciar o servidor Gunicorn
echo "3. Iniciando servidor Gunicorn..."
gunicorn energia_solar.wsgi:application --bind 0.0.0.0:$PORT
