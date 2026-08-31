FROM python:3.14-alpine

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/
COPY . /app

ENV UV_NO_DEV=1

WORKDIR /app
RUN uv sync --locked

EXPOSE $APP_PORT

RUN addgroup -S tfremake \
    && adduser -S tfremake -G tfremake

RUN chown -R tfremake:tfremake /app

USER tfremake

CMD ["uv", "run", "runserver.py"]
