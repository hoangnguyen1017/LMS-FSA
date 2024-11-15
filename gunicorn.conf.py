# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8001"

# number of worker processes
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 20

# Worker class
worker_class = 'gevent'  # use gevent for async IO

# threads for worker
threads = 4

# Timeouts
timeout = 120
keepalive = 5
graceful_timeout = 120

# limit requests
max_requests = 1000
max_requests_jitter = 200

# Buffer size
worker_connections = 1000

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'


# Monitoring
# statsd_host = 'localhost:8125'