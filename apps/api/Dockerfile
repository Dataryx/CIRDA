# Build from repository root:
#   docker build -f apps/api/Dockerfile .
FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app/
COPY packages/cirda-core /app/packages/cirda-core
COPY apps/api /app/apps/api

WORKDIR /app
RUN uv sync --package cirda-api --no-dev

ENV CIRDA_HOST=0.0.0.0 CIRDA_PORT=8000
EXPOSE 8000

WORKDIR /app/apps/api
CMD ["uv", "run", "uvicorn", "cirda_api.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
