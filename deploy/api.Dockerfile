# The API: FastAPI under gunicorn with Uvicorn workers (api/gunicorn.conf.py).
# Built from the repository root, which .dockerignore narrows down:
#
#   docker build -f deploy/api.Dockerfile .
#
# The image also holds the catalog and the question bank, so that seed and
# import-content read the content of the same commit as the code.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# The dependencies in a layer of their own, rebuilt only when the lock
# changes. No dev tools.
COPY api/pyproject.toml api/uv.lock api/.python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

COPY api/ ./
COPY content/catalog.yaml /content/catalog.yaml
COPY content/bank/ /content/bank/

# Commands run from the virtualenv directly: `uv run` would check the lock
# at every start.
ENV PATH="/app/.venv/bin:$PATH" \
    CONTENT_DIR=/content \
    ENVIRONMENT=production \
    LOG_JSON=true

RUN useradd --system --no-create-home --shell /usr/sbin/nologin app
USER app

EXPOSE 8000
CMD ["gunicorn", "-c", "gunicorn.conf.py"]
