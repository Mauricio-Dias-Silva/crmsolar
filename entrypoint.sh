#!/bin/bash
# entrypoint.sh - Script de inicialização para o Cloud Run

# Sair imediatamente se um comando falhar
set -e

# --- 1. CONFIGURAÇÃO DA VARIÁVEL DE CONEXÃO DO CLOUD SQL ---
# O Cloud Run injeta o nome da conexão do Cloud SQL nesta variável.
# Usamos 'nc' para verificar se o socket do BD está ativo.
# O nome da conexão do Cloud SQL (ex: project-id:region:instance-name) é derivado da flag --add-cloudsql-instances.

# A porta 5432 é o padrão do PostgreSQL.
DB_HOST="/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"
DB_PORT=5432 

echo "Iniciando script de entrada. Verificando conexao com Cloud SQL..."

# --- 2. LOOP DE ESPERA (Wait-for-DB) ---
# Espera que o socket do Cloud SQL esteja disponível antes de tentar o 'migrate'.
echo "Esperando a disponibilidade do Cloud SQL..."
# O comando 'nc -z -w 1' verifica se a porta está aberta. 
while ! nc -z -w 1 $DB_HOST $DB_PORT; do  
  echo "Aguardando Cloud SQL..."
  sleep 2
done
echo "Cloud SQL acessível. Continuando..."

# --- 3. EXECUÇÃO DOS COMANDOS DE PRÉ-SERVIÇO ---

# Coletar arquivos estáticos (Resolve o Admin sem CSS)
echo "1. Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

# Executar migrações do banco de dados (Necessário no primeiro deploy)
echo "2. Executando migrações do banco de dados..."
python manage.py migrate --no-input

# --- 4. INICIAR O SERVIDOR ---
echo "3. Iniciando servidor Gunicorn..."
# O Gunicorn escuta a porta definida pelo Cloud Run ($PORT, que é 8080)
gunicorn energia_solar.wsgi:application --bind 0.0.0.0:$PORT
