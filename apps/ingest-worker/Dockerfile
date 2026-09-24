# Build from repository root:
#   docker build -f apps/ingest-worker/Dockerfile .

FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY packages packages
COPY apps/ingest-worker apps/ingest-worker

ENV UV_LINK_MODE=copy
RUN uv sync --package cirda-ingest --no-dev --frozen

FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 1000 cirda \
    && useradd --uid 1000 --gid cirda --create-home --shell /usr/sbin/nologin cirda \
    && pip install --no-cache-dir uv

COPY --from=builder /app /app

COPY apps/ingest-worker/docker-entrypoint.sh /app/apps/ingest-worker/docker-entrypoint.sh
RUN sed -i 's/\r$//' /app/apps/ingest-worker/docker-entrypoint.sh \
    && chmod +x /app/apps/ingest-worker/docker-entrypoint.sh \
    && chown -R cirda:cirda /app

USER cirda

ENV CIRDA_HOST=0.0.0.0 \
    CIRDA_PORT=8081 \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app/apps/ingest-worker
EXPOSE 8081 4318

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=10 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/health')"

ENTRYPOINT ["/app/apps/ingest-worker/docker-entrypoint.sh"]
CMD ["uv", "run", "cirda-ingest"]
