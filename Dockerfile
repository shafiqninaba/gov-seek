FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY . /app

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync

CMD streamlit run --server.port $PORT src/streamlit_app.py
