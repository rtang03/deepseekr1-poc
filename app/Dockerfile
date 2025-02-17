# Build stage
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder
WORKDIR /var/task
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Final stage
FROM public.ecr.aws/docker/library/python:3.12-slim

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.0 /lambda-adapter /opt/extensions/lambda-adapter
ENV PORT=8000 \
    OLLAMA_MODELS=/var/task/.ollama/models

WORKDIR /var/task
COPY --from=builder /root/.local /root/.local
COPY .env entrypoint.sh *.py log_conf.yaml ./

RUN apt-get update && apt-get install -y curl systemctl && \
    curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.5.7 sh && \
    rm -rf /usr/local/lib/ollama/runners/cuda_v11_avx && \
    rm -rf /usr/local/lib/ollama/runners/cuda_v12_avx && \
    rm -rf /usr/local/lib/ollama/runners/rocm_avx && \
    rm /usr/local/lib/ollama/libcublasLt* && \
    rm /usr/local/lib/ollama/libcublas* && \
    rm /usr/local/lib/ollama/libcudart* && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    chmod +x ./entrypoint.sh && \
    mkdir -p /var/task/.ollama/models && \
    adduser --disabled-password --gecos '' appuser

COPY ./.ollama/models/ /var/task/.ollama/models/

USER appuser

# Set entrypoint using exec form
ENTRYPOINT ["./entrypoint.sh"]
