#!/usr/bin/env python3
"""
Test script to verify deployment configuration.
Run this before deploying to catch issues early.
"""

import os
import sys
import subprocess
import tempfile

def test_wsgi_import():
    """Test that WSGI module can be imported."""
    print("Testing WSGI import...")
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test import
        from wsgi import application
        print("✅ WSGI import successful")
        return True
    except Exception as e:
        print(f"❌ WSGI import failed: {e}")
        return False

def test_gunicorn_config():
    """Test that Gunicorn config is valid."""
    print("Testing Gunicorn configuration...")
    try:
        # Test config syntax
        result = subprocess.run([
            'python', '-c', 
            'import gunicorn.config; c = gunicorn.config.Config(); c.set("config", "gunicorn.conf.py")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Gunicorn config is valid")
            return True
        else:
            print(f"❌ Gunicorn config error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Gunicorn config test failed: {e}")
        return False

def test_requirements():
    """Test that all requirements are satisfied."""
    print("Testing requirements...")
    try:
        with open('linguaflow/requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        missing = []
        for req in requirements:
            if req.strip() and not req.startswith('#'):
                package = req.split('==')[0].split('>=')[0].split('<=')[0]
                try:
                    __import__(package.replace('-', '_'))
                except ImportError:
                    missing.append(package)
        
        if missing:
            print(f"❌ Missing packages: {', '.join(missing)}")
            return False
        else:
            print("✅ All requirements satisfied")
            return True
    except Exception as e:
        print(f"❌ Requirements test failed: {e}")
        return False

def test_environment_template():
    """Test environment variable template."""
    print("Testing environment variables...")
    
    required_vars = [
        'FLASK_SECRET_KEY',
        'JWT_SECRET',
        'MONGODB_URI', 
        'GROQ_API_KEY'
    ]
    
    # Check if .env.example exists and has all required vars
    env_example_path = 'linguaflow/.env.example'
    if os.path.exists(env_example_path):
        with open(env_example_path, 'r') as f:
            env_content = f.read()
        
        missing_in_example = []
        for var in required_vars:
            if var not in env_content:
                missing_in_example.append(var)
        
        if missing_in_example:
            print(f"⚠️  Missing in .env.example: {', '.join(missing_in_example)}")
        else:
            print("✅ .env.example contains all required variables")
    else:
        print("⚠️  .env.example not found")
    
    return True

def main():
    """Run all deployment tests."""
    print("🧪 Running deployment tests...\n")
    
    tests = [
        test_requirements,
        test_wsgi_import,
        test_gunicorn_config,
        test_environment_template,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
        print()
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())