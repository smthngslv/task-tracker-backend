from os import cpu_count
from pathlib import Path

import yaml

bind = '0.0.0.0:8000'
workers = cpu_count()
worker_class = 'uvicorn.workers.UvicornWorker'

# Restart workers at least once every 10000 requests.
max_requests = 10000
max_requests_jitter = 1000
# Connection to nginx.
keepalive = 64

logging_config_path = Path('./config/logging.yaml')
if logging_config_path.is_file():
    # Logs config.
    with logging_config_path.open(encoding='UTF-8') as file:
        # Logging config.
        logconfig_dict = yaml.safe_load(file)
