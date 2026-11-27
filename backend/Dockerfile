FROM python:3.13-slim

WORKDIR /srv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv PYTHONUNBUFFERED=1 PATH=/opt/venv/bin:$PATH

RUN pip install --no-cache-dir uv==0.13.1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache

COPY . .
RUN useradd --system --no-create-home app
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
