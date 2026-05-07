# Gunicorn configuration file for LinguaFlow
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Worker processes
workers = 1  # Optimal for free tier
worker_class = "sync"
timeout = 120

# Restart workers to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "linguaflow"

# Preload application
preload_app = True

# Security
forwarded_allow_ips = "*"