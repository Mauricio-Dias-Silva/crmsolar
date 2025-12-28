# 1. Imagem base
FROM python:3.11-slim

# 2. Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# --- INÍCIO DA CORREÇÃO PARA O ERRO DA LIBGOBJECT ---
# Instala as dependências de sistema para o WeasyPrint e GObject
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# --- FIM DA CORREÇÃO ---

# 3. Instalação de dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o código
COPY . .

# 5. Sua lógica de detecção automática do WSGI
RUN WSGI_MODULE="" && \
    WSGI_FILE=$(find . -maxdepth 2 -name "wsgi.py" -not -path "./venv/*" -not -path "./.venv/*" | head -1) && \
    if [ -n "$WSGI_FILE" ]; then \
        WSGI_DIR=$(dirname "$WSGI_FILE" | sed 's|^\./||' | tr '/' '.'); \
        WSGI_MODULE="${WSGI_DIR}.wsgi:application"; \
    fi && \
    if [ -z "$WSGI_MODULE" ]; then WSGI_MODULE="config.wsgi:application"; fi && \
    echo "export WSGI_MODULE=$WSGI_MODULE" > /app/.wsgi_config && \
    echo "[PYTHONJET] WSGI detectado: $WSGI_MODULE"

# 6. Coleta de estáticos (com tratamento de erro)
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# 7. Configuração de porta e execução
ENV PORT=8080
EXPOSE 8080

# Usamos o 'source' (.) para carregar a variável detectada e iniciar o Gunicorn
CMD . /app/.wsgi_config && exec gunicorn $WSGI_MODULE --bind 0.0.0.0:${PORT} --timeout 0
