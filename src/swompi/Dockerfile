FROM python:3.13.11-alpine3.23

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY ../../pyproject.toml ./

RUN pip install --upgrade pip poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

COPY . ./
COPY ../../.env ./

EXPOSE 25851

CMD ["python", "main.py"]