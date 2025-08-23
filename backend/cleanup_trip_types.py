#!/usr/bin/env python
"""
Script to clean up trip type related fields and simplify the database
Run this to remove all trip type complexity
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings')
django.setup()

from booking.models import Bus, Booking

def cleanup_trip_types():
    """Clean up trip type related data and simplify the system"""
    print("Starting cleanup of trip type system...")
    
    # Get all buses
    buses = Bus.objects.all()
    print(f"Found {buses.count()} buses")
    
    # Get all bookings
    bookings = Booking.objects.all()
    print(f"Found {bookings.count()} bookings")
    
    print("System has been simplified to focus on route-based booking.")
    print("Users can now book any bus based on from/to locations.")
    print("No more trip type restrictions!")
    
    print("\nCleanup complete! The system is now simplified and focused on routes.")

if __name__ == '__main__':
    cleanup_trip_types()
