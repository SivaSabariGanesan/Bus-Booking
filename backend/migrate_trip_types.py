#!/usr/bin/env python
"""
Migration script to update existing buses to have proper trip_types
Run this after updating the models to fix existing data
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings')
django.setup()

from booking.models import Bus

def migrate_trip_types():
    """Update existing buses to have proper trip_types"""
    print("Starting trip_types migration...")
    
    # Get all buses
    buses = Bus.objects.all()
    print(f"Found {buses.count()} buses to migrate")
    
    updated_count = 0
    for bus in buses:
        # Check if trip_types needs updating
        if not bus.trip_types or bus.trip_types == '[]' or bus.trip_types == '':
            bus.trip_types = 'RETURN'
            bus.save()
            updated_count += 1
            print(f"Updated bus {bus.bus_no} to have trip_types: {bus.trip_types}")
        else:
            print(f"Bus {bus.bus_no} already has trip_types: {bus.trip_types}")
    
    print(f"Migration complete! Updated {updated_count} buses")

if __name__ == '__main__':
    migrate_trip_types()
