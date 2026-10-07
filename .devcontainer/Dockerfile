FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# psql client for the SQL projects (06, 07); libgomp1 for xgboost
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client libgomp1 \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
