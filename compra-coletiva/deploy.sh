#!/bin/bash

# deploy.sh
# Script de deploy para o VarejoUnido

# --- Configurações ---
# Substitua pelo seu nome de usuário SSH no servidor
SSH_USER="seu_usuario_ssh" 
# Substitua pelo IP ou domínio do seu servidor
SSH_HOST="seu_ip_ou_dominio_do_servidor"
# Caminho absoluto onde o projeto está no servidor
PROJECT_DIR="/var/www/varejounido" 
# Nome do ambiente virtual no servidor
VENV_DIR="$PROJECT_DIR/venv" 
# Caminho para o interpretador Python do ambiente virtual
PYTHON_BIN="$VENV_DIR/bin/python" 
# Caminho para o executável do Django manage.py
MANAGE_PY="$PROJECT_DIR/manage.py" 
# Caminho para o Celery (Celery Beat e Worker)
CELERY_APP="projeto_compra_coletiva" 


echo "--- Iniciando processo de deploy do VarejoUnido ---"

# --- 1. Conectar via SSH e Puxar o Código Atualizado ---
echo "1. Conectando via SSH e puxando o código mais recente..."
ssh $SSH_USER@$SSH_HOST << EOF
  cd $PROJECT_DIR || { echo "Erro: Diretório do projeto não encontrado em $PROJECT_DIR"; exit 1; }
  git pull origin main || { echo "Erro: Falha ao puxar o código do Git."; exit 1; }
  echo "Código atualizado com sucesso."
EOF
if [ $? -ne 0 ]; then
  echo "Erro no passo SSH/Git Pull. Saindo."
  exit 1
fi
echo "Conexão SSH e Git Pull concluídos."

# --- 2. Atualizar Dependências Python ---
echo "2. Atualizando dependências Python..."
ssh $SSH_USER@$SSH_HOST "$PYTHON_BIN -m pip install --upgrade pip"
ssh $SSH_USER@$SSH_HOST "$PYTHON_BIN -m pip install -r $PROJECT_DIR/requirements.txt || { echo 'Erro: Falha ao instalar dependências.'; exit 1; }"
if [ $? -ne 0 ]; then
  echo "Erro na atualização de dependências. Saindo."
  exit 1
fi
echo "Dependências Python atualizadas."

# --- 3. Coletar Arquivos Estáticos ---
echo "3. Coletando arquivos estáticos..."
ssh $SSH_USER@$SSH_HOST "$PYTHON_BIN $MANAGE_PY collectstatic --noinput || { echo 'Erro: Falha ao coletar estáticos.'; exit 1; }"
if [ $? -ne 0 ]; then
  echo "Erro na coleta de estáticos. Saindo."
  exit 1
fi
echo "Arquivos estáticos coletados."

# --- 4. Aplicar Migrações do Banco de Dados ---
echo "4. Aplicando migrações do banco de dados..."
ssh $SSH_USER@$SSH_HOST "$PYTHON_BIN $MANAGE_PY migrate || { echo 'Erro: Falha ao aplicar migrações.'; exit 1; }"
if [ $? -ne 0 ]; then
  echo "Erro nas migrações. Saindo."
  exit 1
fi
echo "Migrações aplicadas."

# --- 5. Reiniciar Serviços de Produção (Gunicorn, Celery Worker, Celery Beat) ---
echo "5. Reiniciando serviços de produção..."
# Isso assume que você configurou systemd ou supervisor para gerenciar esses serviços
ssh $SSH_USER@$SSH_HOST "sudo systemctl restart gunicorn.service || { echo 'Aviso: Falha ao reiniciar Gunicorn. Verifique o serviço.'; }"
ssh $SSH_USER@$SSH_HOST "sudo systemctl restart celery_worker.service || { echo 'Aviso: Falha ao reiniciar Celery Worker. Verifique o serviço.'; }"
ssh $SSH_USER@$SSH_HOST "sudo systemctl restart celery_beat.service || { echo 'Aviso: Falha ao reiniciar Celery Beat. Verifique o serviço.'; }"

echo "--- Deploy do VarejoUnido concluído com sucesso! ---"