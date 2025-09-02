#!/usr/bin/env python3
"""
Test script to debug Django startup issues on Railway
"""

import os
import sys
import django
from pathlib import Path

def test_django_startup():
    """Test if Django can start with production settings"""
    print("🧪 Testing Django startup...")
    
    # Set environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings_production')
    
    try:
        # Test Django setup
        print("📋 Setting up Django...")
        django.setup()
        print("✅ Django setup successful")
        
        # Test database connection
        print("🗄️ Testing database connection...")
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection successful")
        
        # Test URL configuration
        print("🔗 Testing URL configuration...")
        from django.urls import reverse
        from django.test import Client
        client = Client()
        
        # Test health endpoint
        response = client.get('/health/')
        print(f"✅ Health endpoint test: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_django_startup()
    sys.exit(0 if success else 1)
