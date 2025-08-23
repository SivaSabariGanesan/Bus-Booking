#!/usr/bin/env python
"""
Script to update all existing buses to support all trip types without restrictions
Run this to remove all trip type limitations
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings')
django.setup()

from booking.models import Bus

def update_all_buses():
    """Update all buses to support all trip types without restrictions"""
    print("Starting update to remove trip type restrictions...")
    
    # Get all buses
    buses = Bus.objects.all()
    print(f"Found {buses.count()} buses to update")
    
    updated_count = 0
    for bus in buses:
        # Update trip_types to show no restrictions
        bus.trip_types = 'ALL'
        bus.save()
        updated_count += 1
        print(f"Updated bus {bus.bus_no} to support all trip types without restrictions")
    
    print(f"Update complete! {updated_count} buses now support all trip types without restrictions")
    print("Users can now book any bus for any trip type!")

if __name__ == '__main__':
    update_all_buses()
