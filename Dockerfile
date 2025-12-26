FROM python:3.13.11-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt update && \
    apt install -y --no-install-recommends \
    git \
    curl \
    ca-certificates && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list && \
    apt update && \
    apt install -y --no-install-recommends docker-ce-cli docker-buildx-plugin && \
    pip install --no-cache-dir --upgrade pip poetry && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

COPY ./src/swompi ./swompi

RUN poetry install --no-interaction

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]