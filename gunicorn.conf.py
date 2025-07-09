# Gunicorn configuration for Google Cloud Platform deployment
# Optimized for PostgreSQL and production workloads

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout settings (increased for large file processing)
timeout = 300  # 5 minutes for large satellite files
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "tropical-cloud-detection"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (handled by Google Cloud load balancer)
keyfile = None
certfile = None

# Security
limit_request_line = 8192
limit_request_fields = 1000
limit_request_field_size = 32768  # Increased for larger file uploads

# Memory management (important for large file processing)
preload_app = True
max_requests_jitter = 50

# Environment variables
raw_env = [
    "DJANGO_SETTINGS_MODULE=cloud_detection_portal.settings",
]

# Worker timeout for large file processing
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files

# Enable worker recycling to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging configuration
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
            'qualname': 'gunicorn.error'
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
            'qualname': 'gunicorn.access'
        },
    }
} 