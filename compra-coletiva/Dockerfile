# Dockerfile

# Usa uma imagem oficial do Python como base
FROM python:3.11-slim-buster

# Define variáveis de ambiente para Python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo requirements.txt para o contêiner
COPY requirements.txt /app/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o contêiner
COPY . /app/

# Define o comando padrão para rodar a aplicação (pode ser sobrescrito pelo docker-compose)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]