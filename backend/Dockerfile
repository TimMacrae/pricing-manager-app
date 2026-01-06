FROM python:3.12-slim

WORKDIR /app

# system deps (MySQL client libs, build tools)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# install uv
RUN pip install --no-cache-dir uv

# copy dependency files first (for caching)
COPY pyproject.toml uv.lock* /app/

# install deps (if uv.lock exists, it will use it)
RUN uv sync

# copy project
COPY . /app