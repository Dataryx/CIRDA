# Build from repository root:
#   docker build -f apps/ingest-worker/Dockerfile .
FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app/
COPY packages/cirda-core /app/packages/cirda-core
COPY apps/ingest-worker /app/apps/ingest-worker

WORKDIR /app
RUN uv sync --package cirda-ingest --no-dev

ENV CIRDA_HOST=0.0.0.0 CIRDA_PORT=8081
EXPOSE 8081 4318

WORKDIR /app/apps/ingest-worker
CMD ["uv", "run", "cirda-ingest"]
