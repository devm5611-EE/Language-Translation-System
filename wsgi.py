#!/usr/bin/env python3
"""
WSGI entry point for LinguaFlow application.
This file is used by Gunicorn and other WSGI servers.
"""

import os
import sys

# Add the linguaflow directory to Python path
linguaflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linguaflow')
sys.path.insert(0, linguaflow_path)

# Import and create the Flask application
from app import create_app

# Create the WSGI application
application = create_app()

if __name__ == "__main__":
    application.run()