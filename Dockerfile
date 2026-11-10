# Build from repository root: docker build -t solo-ai-usage .
# Snapshots are never baked into this image; mount sanitized state read-only.
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /usr/local/bin/uv
# Dependencies come from uv.lock (--frozen), so every build installs the versions CI tested.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 AI_USAGE_API_HOST=0.0.0.0 AI_USAGE_API_ENV=production AI_USAGE_STATE_DIR=/app/state \
    UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv PATH=/opt/venv/bin:$PATH
WORKDIR /app
COPY vendor/service-auth /app/vendor/service-auth
COPY pyproject.toml uv.lock server.py model.py collector.py error_reporting.py /app/
RUN uv sync --frozen --no-dev --no-editable --no-cache --python /usr/local/bin/python3
RUN useradd --system --uid 10001 app
# Image hardening: take Debian security fixes newer than the base tag, then drop the base
# image's pip (the app runs from its installed environment; pip's vendored urllib3/msgpack/
# setuptools copies are what the Trivy image scan flags).
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && /usr/local/bin/python3 -m pip uninstall -y --disable-pip-version-check pip
USER app
EXPOSE 3520
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD python -c "import os, urllib.request; port=os.environ.get('AI_USAGE_API_PORT', os.environ.get('PORT', '3520')); urllib.request.urlopen('http://127.0.0.1:'+port+'/ready', timeout=2)"
CMD ["python", "/app/server.py"]
