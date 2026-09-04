# deploy/gunicorn.conf.py
#
# Gunicorn configuration for the School-app Django project.
# Referenced by the systemd service:
#   gunicorn -c deploy/gunicorn.conf.py project.wsgi:application

import multiprocessing
import os

# Bind to a local TCP port that Nginx proxies to. Loopback only, so it is
# never exposed directly to the internet. Override with GUNICORN_BIND.
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8000")

# Worker processes: (2 x CPU cores) + 1 is a good default. Override with
# GUNICORN_WORKERS for small/large instances.
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Recycle workers periodically to guard against slow memory leaks.
max_requests = 1000
max_requests_jitter = 50

# Request/worker timeouts.
timeout = 60
keepalive = 5

# Log access + errors to stdout/stderr so `journalctl -u gunicorn` captures them.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")

proc_name = "school-app"
