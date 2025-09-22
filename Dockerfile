# Etapa 1: Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Definir variáveis de ambiente para garantir que os logs do Python apareçam imediatamente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Etapa 2: Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Etapa 3: Copiar o requirements.txt e instalar as dependências
# Copiamos este arquivo primeiro para aproveitar o cache de camadas do Docker.
# A camada de dependências só será reconstruída se o requirements.txt mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 4: Copiar o restante dos arquivos da aplicação
# Isso inclui app.py, agent_manager.py, .env, e as pastas faiss_index/ e pdfs/
COPY . .

# Etapa 5: Expor a porta que a aplicação irá rodar
# Usamos 8000, que é a porta padrão definida no seu app.py
EXPOSE 8000

# Etapa 6: Usar gunicorn para iniciar a aplicação
# O comando "app:app" refere-se ao objeto 'app' dentro do arquivo 'app.py'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
