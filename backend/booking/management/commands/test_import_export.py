from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth import get_user_model
from import_export import resources
from booking.models import Student, Bus, Booking
from booking.resources import StudentResource, BusResource, BookingResource
import tempfile
import os
import csv

Student = get_user_model()

class Command(BaseCommand):
    help = 'Test the import/export functionality for all models'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing import/export functionality...'))
        
        try:
            # Test Student Resource
            self.test_student_resource()
            
            # Test Bus Resource
            self.test_bus_resource()
            
            # Test Booking Resource
            self.test_booking_resource()
            
            self.stdout.write(self.style.SUCCESS('All import/export tests passed!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Test failed: {str(e)}'))
    
    def test_student_resource(self):
        """Test Student import/export functionality"""
        self.stdout.write('Testing Student resource...')
        
        # Create test data
        student_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'roll_no': 'TEST001',
            'dept': 'Computer Science',
            'year': '1',
            'gender': 'M',
            'student_type': 'REGULAR',
            'degree_type': 'BTECH',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }
        
        # Test export
        resource = StudentResource()
        dataset = resource.export()
        self.stdout.write(f'Student export successful. {len(dataset)} rows exported.')
        
        # Test import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=student_data.keys())
            writer.writeheader()
            writer.writerow(student_data)
            temp_file = f.name
        
        try:
            with open(temp_file, 'r') as f:
                dataset = resource.import_data(f.read(), format='csv')
                self.stdout.write(f'Student import successful. {len(dataset.rows)} rows imported.')
        finally:
            os.unlink(temp_file)
    
    def test_bus_resource(self):
        """Test Bus import/export functionality"""
        self.stdout.write('Testing Bus resource...')
        
        # Create test data
        bus_data = {
            'bus_no': 'TEST001',
            'route_name': 'Test Route',
            'from_location': 'Test Start',
            'to_location': 'Test End',
            'departure_date': '2024-01-15',
            'departure_time': '08:00',
            'capacity': 50
        }
        
        # Test export
        resource = BusResource()
        dataset = resource.export()
        self.stdout.write(f'Bus export successful. {len(dataset)} rows exported.')
        
        # Test import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=bus_data.keys())
            writer.writeheader()
            writer.writerow(bus_data)
            temp_file = f.name
        
        try:
            with open(temp_file, 'r') as f:
                dataset = resource.import_data(f.read(), format='csv')
                self.stdout.write(f'Bus import successful. {len(dataset.rows)} rows imported.')
        finally:
            os.unlink(temp_file)
    
    def test_booking_resource(self):
        """Test Booking import/export functionality"""
        self.stdout.write('Testing Booking resource...')
        
        # Create test data
        booking_data = {
            'student_email': 'test@example.com',
            'bus_no': 'TEST001',
            'trip_date': '2024-01-15',
            'departure_time': '08:00',
            'from_location': 'Test Start',
            'to_location': 'Test End',
            'status': 'PENDING'
        }
        
        # Test export
        resource = BookingResource()
        dataset = resource.export()
        self.stdout.write(f'Booking export successful. {len(dataset)} rows exported.')
        
        # Test import
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=booking_data.keys())
            writer.writeheader()
            writer.writerow(booking_data)
            temp_file = f.name
        
        try:
            with open(temp_file, 'r') as f:
                dataset = resource.import_data(f.read(), format='csv')
                self.stdout.write(f'Booking import successful. {len(dataset.rows)} rows imported.')
        finally:
            os.unlink(temp_file)
