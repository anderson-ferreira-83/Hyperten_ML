# Dockerfile otimizado para AWS Lambda usando packages pré-compilados
FROM public.ecr.aws/lambda/python:3.11

# Copiar código primeiro
COPY 06_api ${LAMBDA_TASK_ROOT}/06_api
COPY 05_artifacts ${LAMBDA_TASK_ROOT}/05_artifacts
COPY 07_web ${LAMBDA_TASK_ROOT}/07_web
COPY 08_src ${LAMBDA_TASK_ROOT}/08_src

# Instalar dependências leves primeiro
RUN pip install --no-cache-dir --target "${LAMBDA_TASK_ROOT}" \
    mangum==0.17.0 \
    fastapi \
    uvicorn \
    pydantic \
    joblib

# Instalar pacotes científicos usando wheels pré-compilados
RUN pip install --no-cache-dir --target "${LAMBDA_TASK_ROOT}" \
    --only-binary=:all: \
    numpy \
    pandas \
    scikit-learn

# Criar handler Lambda
RUN echo 'import sys' > ${LAMBDA_TASK_ROOT}/lambda_handler.py && \
    echo 'sys.path.insert(0, "/var/task")' >> ${LAMBDA_TASK_ROOT}/lambda_handler.py && \
    echo 'sys.path.insert(0, "/var/task/06_api")' >> ${LAMBDA_TASK_ROOT}/lambda_handler.py && \
    echo 'from mangum import Mangum' >> ${LAMBDA_TASK_ROOT}/lambda_handler.py && \
    echo 'from main import app' >> ${LAMBDA_TASK_ROOT}/lambda_handler.py && \
    echo 'handler = Mangum(app, lifespan="off")' >> ${LAMBDA_TASK_ROOT}/lambda_handler.py

CMD [ "lambda_handler.handler" ]
