from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from booking.models import Student, Bus, Booking, BookingOTP, Stop
import random


class Command(BaseCommand):
    help = 'Create sample bookings with students, buses, and bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample bookings to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Create sample students if they don't exist
        students_data = [
            {
                'email': 'john.doe@rec.edu.in',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '9876543210',
                'year': '3',
                'roll_no': 'REC2021001',
                'dept': 'Computer Science',
                'gender': 'M'
            },
            {
                'email': 'jane.smith@rec.edu.in',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '9876543211',
                'year': '2',
                'roll_no': 'REC2022001',
                'dept': 'Electrical Engineering',
                'gender': 'F'
            },
            {
                'email': 'mike.johnson@rec.edu.in',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'phone_number': '9876543212',
                'year': '4',
                'roll_no': 'REC2020001',
                'dept': 'Mechanical Engineering',
                'gender': 'M'
            },
            {
                'email': 'sarah.wilson@rec.edu.in',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'phone_number': '9876543213',
                'year': '1',
                'roll_no': 'REC2023001',
                'dept': 'Civil Engineering',
                'gender': 'F'
            },
            {
                'email': 'david.brown@rec.edu.in',
                'first_name': 'David',
                'last_name': 'Brown',
                'phone_number': '9876543214',
                'year': '3',
                'roll_no': 'REC2021002',
                'dept': 'Computer Science',
                'gender': 'M'
            }
        ]
        
        students = []
        for student_data in students_data:
            student, created = Student.objects.get_or_create(
                email=student_data['email'],
                defaults=student_data
            )
            if created:
                student.set_password('password123')
                student.save()
                self.stdout.write(f'Created student: {student.full_name}')
            students.append(student)
        
        # Get existing buses
        buses = list(Bus.objects.all())
        if not buses:
            self.stdout.write(self.style.ERROR('No buses found. Please create buses first.'))
            return
        
        # Create sample stops if they don't exist
        for bus in buses:
            stops_data = [
                {'stop_name': 'REC College', 'location': 'REC College', 'is_pickup': True, 'is_dropoff': False},
                {'stop_name': 'Chengalpattu', 'location': 'Chengalpattu', 'is_pickup': False, 'is_dropoff': True},
                {'stop_name': 'Tambaram', 'location': 'Tambaram', 'is_pickup': True, 'is_dropoff': True},
            ]
            
            for stop_data in stops_data:
                Stop.objects.get_or_create(
                    bus=bus,
                    stop_name=stop_data['stop_name'],
                    location=stop_data['location'],
                    defaults={
                        'is_pickup': stop_data['is_pickup'],
                        'is_dropoff': stop_data['is_dropoff'],
                        'is_active': True
                    }
                )
        
        # Create sample bookings
        statuses = ['pending', 'confirmed']
        created_count = 0
        
        for i in range(count):
            if created_count >= count:
                break
                
            student = random.choice(students)
            bus = random.choice(buses)
            
            # Check if student already has a booking for this bus
            if Booking.objects.filter(student=student, bus=bus).exists():
                continue
            
            # Create booking with random status
            status = random.choice(statuses)
            
            # Set trip date to tomorrow or next week
            if random.choice([True, False]):
                trip_date = timezone.now().date() + timedelta(days=1)  # Tomorrow
            else:
                trip_date = timezone.now().date() + timedelta(days=7)  # Next week
            
            # Get a random stop for this bus
            stops = list(Stop.objects.filter(bus=bus, is_pickup=True))
            selected_stop = random.choice(stops) if stops else None
            
            booking = Booking.objects.create(
                student=student,
                bus=bus,
                trip_date=trip_date,
                departure_time=bus.departure_time,
                from_location=bus.from_location,
                to_location=bus.to_location,
                selected_stop=selected_stop,
                status=status
            )
            
            # Create OTP for pending bookings
            if status == 'pending':
                otp_code = ''.join(random.choices('0123456789', k=6))
                expires_at = timezone.now() + timedelta(minutes=15)
                
                BookingOTP.objects.create(
                    booking=booking,
                    otp_code=otp_code,
                    expires_at=expires_at,
                    verified=False
                )
                
                self.stdout.write(f'Created pending booking: {student.full_name} → {bus.route_name} (OTP: {otp_code})')
            else:
                self.stdout.write(f'Created confirmed booking: {student.full_name} → {bus.route_name}')
            
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample bookings!')
        )
        
        # Display summary
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        
        self.stdout.write(f'\nBooking Summary:')
        self.stdout.write(f'Total Bookings: {total_bookings}')
        self.stdout.write(f'Pending: {pending_bookings}')
        self.stdout.write(f'Confirmed: {confirmed_bookings}')
