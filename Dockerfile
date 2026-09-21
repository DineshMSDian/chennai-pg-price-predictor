# stage 1: build

FROM python:3.12-slim AS builder
WORKDIR /api-builder
COPY pyproject.toml uv.lock ./
RUN pip install uv
RUN uv sync --frozen --no-dev --group api --no-install-project

# stage 2: runtime

FROM python:3.12-slim
WORKDIR /api-runtime

COPY --from=builder /api-builder/.venv /api-runtime/.venv
COPY api/ ./api/
COPY models ./models/
COPY src/ ./src/

ENV PATH="/api-runtime/.venv/bin:$PATH"

EXPOSE 8000
CMD [ "python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]