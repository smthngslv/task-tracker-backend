FROM python:3.10
WORKDIR /app

# Environment.
COPY ./docker/requirements.txt /tmp
RUN python -m venv .venv && \
    ./.venv/bin/python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    ./.venv/bin/python -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Actually, we do not need root.
RUN groupadd app && useradd app -g app

# App.
COPY ./task_tracker_backend ./task_tracker_backend
COPY ./config ./config

# Run.
USER app
EXPOSE 8000
ENTRYPOINT ["./.venv/bin/gunicorn", "--config", "./config/gunicorn.conf.py", "task_tracker_backend.api:app"]
