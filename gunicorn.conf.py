"""
Gunicorn configuration for production deployment on Render
Optimized for cloud detection processing with large files
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:10000"
backlog = 2048

# Worker processes
workers = 1  # Single worker to avoid memory issues on free tier
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minutes for large file processing
keepalive = 2

# Memory management
max_requests = 50  # Restart worker after 50 requests
max_requests_jitter = 10  # Add randomness to prevent thundering herd
preload_app = True

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "tropical_cloud_detection"

# Worker process lifecycle
def when_ready(server):
    server.log.info("Tropical Cloud Detection Server is ready. Listening on: %s", server.address)

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")
    
def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal") 