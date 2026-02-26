FROM python:3.14-slim as builder

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN pip install poetry==2.3.2 && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-root --without dev

FROM python:3.14-slim

WORKDIR /app
ENV PYTHONPATH=/app/src
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
COPY . .

CMD ["python", "-m", "uvicorn", "app.service:app", "--host", "0.0.0.0", "--port", "8000"]
