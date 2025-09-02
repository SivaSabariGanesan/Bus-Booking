#!/usr/bin/env python3
"""
Test script to verify the build configuration works correctly.
This script can be run locally to test the same commands that will run in production.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=check, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        if check:
            raise
        return e

def test_build():
    """Test the build configuration."""
    print("🧪 Testing build configuration...")
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Backend directory not found. Please run from project root.")
        return False
    
    # Check if requirements file exists
    if not Path("backend/requirements_production.txt").exists():
        print("❌ requirements_production.txt not found.")
        return False
    
    # Check if manage.py exists
    if not Path("backend/manage.py").exists():
        print("❌ manage.py not found in backend directory.")
        return False
    
    # Check if settings_production.py exists
    if not Path("backend/transport_booking/settings_production.py").exists():
        print("❌ settings_production.py not found.")
        return False
    
    print("✅ All required files found.")
    
    # Test Django check command
    print("\n🔍 Testing Django configuration...")
    try:
        result = run_command(
            "python manage.py check --settings=transport_booking.settings_production",
            cwd="backend"
        )
        print("✅ Django configuration check passed.")
    except subprocess.CalledProcessError:
        print("❌ Django configuration check failed.")
        return False
    
    # Test collectstatic (dry run)
    print("\n📁 Testing static files collection...")
    try:
        result = run_command(
            "python manage.py collectstatic --settings=transport_booking.settings_production --noinput --dry-run",
            cwd="backend"
        )
        print("✅ Static files collection test passed.")
    except subprocess.CalledProcessError:
        print("❌ Static files collection test failed.")
        return False
    
    print("\n🎉 All tests passed! Build configuration is ready.")
    return True

if __name__ == "__main__":
    success = test_build()
    sys.exit(0 if success else 1)
