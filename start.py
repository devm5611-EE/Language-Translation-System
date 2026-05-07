#!/usr/bin/env python3
"""
Startup script for LinguaFlow application.
This script helps debug deployment issues and provides better error messages.
"""

import os
import sys
import logging

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'FLASK_SECRET_KEY',
        'JWT_SECRET', 
        'MONGODB_URI',
        'GROQ_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before starting the application.")
        return False
    
    print("✓ All required environment variables are set")
    return True

def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import flask
        import pymongo
        import groq
        import redis
        print("✓ All required dependencies are available")
        return True
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        print("Please install dependencies with: pip install -r linguaflow/requirements.txt")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting LinguaFlow application...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Add linguaflow to Python path
    linguaflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linguaflow')
    sys.path.insert(0, linguaflow_path)
    
    try:
        from app import create_app
        app = create_app()
        print("✓ Flask application created successfully")
        
        # Test database connection
        try:
            from database.mongodb import get_db
            db = get_db()
            db.admin.command('ping')
            print("✓ Database connection successful")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
        
        # Test Redis connection
        try:
            import redis
            from config import Config
            redis_client = redis.from_url(Config.REDIS_URL, socket_connect_timeout=2)
            redis_client.ping()
            print("✓ Redis connection successful")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e} (will use in-memory fallback)")
        
        print("🎉 Application startup completed successfully!")
        return app
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    app = main()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)