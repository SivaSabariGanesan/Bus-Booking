#!/usr/bin/env python
"""
Script to add departure dates to existing buses
Run this to set departure dates for existing buses
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings')
django.setup()

from booking.models import Bus
from django.utils import timezone
from datetime import timedelta

def add_departure_dates():
    """Add departure dates to existing buses"""
    print("Starting to add departure dates to existing buses...")
    
    # Get all buses
    buses = Bus.objects.all()
    print(f"Found {buses.count()} buses to update")
    
    if buses.count() == 0:
        print("No buses found in the database.")
        return
    
    # Set different departure dates for variety
    today = timezone.now().date()
    dates_to_use = [
        today,  # Today
        today + timedelta(days=1),  # Tomorrow
        today + timedelta(days=2),  # Day after tomorrow
        today + timedelta(days=7),  # Next week
        today + timedelta(days=14),  # Two weeks from now
    ]
    
    updated_count = 0
    for i, bus in enumerate(buses):
        # Cycle through the dates
        departure_date = dates_to_use[i % len(dates_to_use)]
        bus.departure_date = departure_date
        bus.save()
        updated_count += 1
        print(f"Updated bus {bus.bus_no} to depart on {departure_date}")
    
    print(f"\nUpdate complete! {updated_count} buses now have departure dates.")
    print("You can now manage departure dates in the admin interface.")

if __name__ == '__main__':
    add_departure_dates()
