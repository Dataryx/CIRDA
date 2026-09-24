# Build from repository root:
#   docker build -f apps/api/Dockerfile .

FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY packages packages
COPY apps/api apps/api

ENV UV_LINK_MODE=copy
RUN uv sync --package cirda-api --no-dev --frozen

FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 cirda \
    && useradd --uid 1000 --gid cirda --create-home --shell /usr/sbin/nologin cirda \
    && pip install --no-cache-dir uv

COPY --from=builder /app /app

COPY apps/api/docker-entrypoint.sh /app/apps/api/docker-entrypoint.sh
RUN sed -i 's/\r$//' /app/apps/api/docker-entrypoint.sh \
    && chmod +x /app/apps/api/docker-entrypoint.sh \
    && chown -R cirda:cirda /app

USER cirda

ENV CIRDA_HOST=0.0.0.0 \
    CIRDA_PORT=8000 \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app/apps/api
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=10 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')"

ENTRYPOINT ["/app/apps/api/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "cirda_api.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
