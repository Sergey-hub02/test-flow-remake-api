FROM python:3.14-alpine

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/
COPY . /app

ENV UV_NO_DEV=1

WORKDIR /app
RUN uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE $APP_PORT
CMD ["uv", "run", "runserver.py"]
