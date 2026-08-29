FROM python:3.11-slim

WORKDIR /app

ENV UV_HTTP_TIMEOUT=600
ENV UV_HTTP_RETRIES=10

COPY . .

RUN pip install uv
RUN uv sync --frozen


CMD ["uv", "run", "python", "src/reqs/main.py"]