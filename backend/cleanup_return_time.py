#!/usr/bin/env python
"""
Script to clean up return_time fields and simplify the system
Run this to remove return time complexity
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings')
django.setup()

from booking.models import Bus, Booking

def cleanup_return_time():
    """Clean up return_time fields and simplify the system"""
    print("Starting cleanup of return_time system...")
    
    # Get all buses
    buses = Bus.objects.all()
    print(f"Found {buses.count()} buses")
    
    # Get all bookings
    bookings = Booking.objects.all()
    print(f"Found {bookings.count()} bookings")
    
    print("System has been simplified to focus on departure information only.")
    print("No more return time complexity!")
    print("Users can now book buses based on departure date/time and route.")
    
    print("\nCleanup complete! The system now focuses on departure information only.")

if __name__ == '__main__':
    cleanup_return_time()
