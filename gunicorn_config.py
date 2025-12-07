# gunicorn_config.py
import multiprocessing

# Bind to the port specified by the PORT environment variable
bind = "0.0.0.0:" + str(int(os.environ.get("PORT", 5000)))

# Number of workers
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = 'sync'

# Timeout
timeout = 120

# Keep alive
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'