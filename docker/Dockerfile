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

CMD ["gunicorn", "config.wsgi:application", "--workers", "4", "--bind", "0.0.0.0:8000", "--timeout", "60"]

COPY ./docker/entrypoint.sh .

ENTRYPOINT ["sh", "entrypoint.sh"]
