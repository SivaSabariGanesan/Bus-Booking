#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings')
django.setup()

from booking.models import Bus

print("=== BUS DATABASE CHECK ===")
print(f"Total buses in database: {Bus.objects.count()}")

print("\n=== FROM REC Buses (Outbound) ===")
from_rec_buses = Bus.objects.filter(from_location__icontains='REC')
if from_rec_buses.exists():
    for bus in from_rec_buses:
        print(f"- {bus.bus_no}: {bus.from_location} → {bus.to_location}")
else:
    print("No FROM REC buses found!")

print("\n=== TO REC Buses (Return) ===")
to_rec_buses = Bus.objects.filter(to_location__icontains='REC')
if to_rec_buses.exists():
    for bus in to_rec_buses:
        print(f"- {bus.bus_no}: {bus.from_location} → {bus.to_location}")
else:
    print("No TO REC buses found!")

print("\n=== All Buses ===")
all_buses = Bus.objects.all()
if all_buses.exists():
    for bus in all_buses:
        print(f"- {bus.bus_no}: {bus.from_location} → {bus.to_location}")
else:
    print("No buses found in database!")
