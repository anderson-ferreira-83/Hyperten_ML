# Dockerfile para deploy na AWS Lambda
# Imagem base Python slim para reduzir tamanho
FROM python:3.11-slim

# Configurar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .

# Criar requirements mínimo para produção (apenas o necessário para API)
RUN echo "fastapi>=0.110.0" > requirements_prod.txt && \
    echo "uvicorn>=0.25.0" >> requirements_prod.txt && \
    echo "pandas>=1.5.0" >> requirements_prod.txt && \
    echo "numpy>=1.21.0" >> requirements_prod.txt && \
    echo "scikit-learn>=1.1.0" >> requirements_prod.txt && \
    echo "joblib>=1.1.0" >> requirements_prod.txt && \
    echo "pydantic>=2.0.0" >> requirements_prod.txt && \
    echo "mangum>=0.17.0" >> requirements_prod.txt

# Instalar dependências de produção
RUN pip install --no-cache-dir -r requirements_prod.txt

# Copiar código da API e artefatos do modelo
COPY 06_api ./06_api
COPY 05_artifacts ./05_artifacts
COPY 07_web ./07_web
COPY 08_src ./08_src

# Expor porta (para testes locais)
EXPOSE 8000

# Comando para iniciar o servidor
# Para Lambda, será sobrescrito pelo handler do Mangum
CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "06_api", "--host", "0.0.0.0", "--port", "8000"]
