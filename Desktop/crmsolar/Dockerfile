
# Usar uma imagem base oficial do Python
FROM python:3.12-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir o diretório de trabalho no container
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requisitos
COPY requirements.txt /app/

# Instalar as dependências do Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar o restante do código do projeto
COPY . /app/

# Coletar arquivos estáticos (se possível durante o build, senão no entrypoint)
# RUN python manage.py collectstatic --noinput

# Expor a porta que o Gunicorn vai rodar (embora o Cloud Run injete a PORT)
EXPOSE 8080

# Comando para iniciar a aplicação usando Gunicorn
CMD ["gunicorn", "energia_solar.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "0"]
