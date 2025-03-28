FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 POETRY_VERSION=1.8.4

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

ARG user=shop_user
ARG group=shop
RUN groupadd -r ${group} && useradd -r -g ${group} ${user}

WORKDIR /usr/src/app

RUN python -m pip install --upgrade pip poetry

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi

COPY ./app .

RUN chown -R ${user}:${group} ./

USER ${user}

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]

COPY ./docker/entrypoint.sh .

ENTRYPOINT ["sh", "entrypoint.sh"]
