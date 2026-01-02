#!/bin/bash
# entrypoint.sh - Gerente de Inicialização PythonJet

# Para imediatamente se houver erro
set -e

echo "[PYTHONJET] Iniciando Deploy..."

# 1. Coletar arquivos estáticos (CSS/JS do Admin e Site)
echo "[PYTHONJET] Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# 2. Rodar migrações de banco de dados
echo "[PYTHONJET] Executando migrações..."
python manage.py migrate --no-input

# 3. Iniciar o servidor web
echo "[PYTHONJET] Iniciando Gunicorn na porta $PORT..."
# IMPORTANTE: Substitua 'energia_solar.wsgi' pelo nome do seu projeto (ex: core.wsgi)
gunicorn energia_solar.wsgi:application --bind 0.0.0.0:$PORT
