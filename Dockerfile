FROM oven/bun:1 AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/bun.lock frontend/bunfig.toml ./
RUN bun install --frozen-lockfile

COPY frontend/ ./
RUN env -u LOVABLE_SANDBOX -u DEV_SERVER__PROJECT_PATH bun run build

FROM node:22-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor ca-certificates gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv python install 3.13 \
    && uv sync --frozen --no-dev --no-install-project --python 3.13

COPY backend/src/ ./src/
RUN uv sync --frozen --no-dev --python 3.13

COPY --from=frontend-build /app/frontend/.output /app/frontend/.output
COPY nginx/nginx.conf /etc/nginx/nginx.conf.template
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/entrypoint.sh /app/docker/entrypoint.sh

ENV NODE_ENV=production \
    HOST=127.0.0.1 \
    PORT=80 \
    NITRO_PORT=3000 \
    PYTHONUNBUFFERED=1

EXPOSE 80 10000

CMD ["/bin/sh", "/app/docker/entrypoint.sh"]
