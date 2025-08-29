from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


class StudentManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Student(AbstractBaseUser):
    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES)
    roll_no = models.CharField(max_length=20, unique=True)
    dept = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = StudentManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'roll_no']
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_no})"
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_active_booking(self):
        from django.utils import timezone
        from datetime import datetime, time
        now = timezone.localtime(timezone.now())
        # Only consider bookings as active if their trip_date and departure_time are in the future
        for booking in self.booking_set.filter(status__in=['pending', 'confirmed']):
            trip_datetime = timezone.make_aware(datetime.combine(booking.trip_date, booking.departure_time))
            if trip_datetime > now:
                return True
        return False


class Bus(models.Model):
    bus_no = models.CharField(max_length=20, unique=True)
    route_name = models.CharField(max_length=100)
    from_location = models.CharField(max_length=100, default="")
    to_location = models.CharField(max_length=100, default="")
    departure_date = models.DateField(default=timezone.now, help_text="Date when this bus is available for departure")
    departure_time = models.TimeField()
    capacity = models.PositiveIntegerField()
    is_booking_open = models.BooleanField(default=True, help_text="If disabled, this bus cannot be booked")
    
    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'
    
    def __str__(self):
        return f"{self.bus_no} - {self.route_name}"
    
    @property
    def available_seats(self):
        return self.capacity - self.booking_set.filter(status='confirmed').count()
    
    @property
    def route_display(self):
        """Display route in a user-friendly format"""
        return f"{self.from_location} → {self.to_location}"
    
    @property
    def is_full(self):
        return self.booking_set.filter(status='confirmed').count() >= self.capacity
    
    def is_available_for_date(self, target_date):
        """Check if bus is available for departure on a specific date"""
        return self.departure_date == target_date
    
    def get_departure_info(self):
        """Get formatted departure information"""
        return {
            'date': self.departure_date.strftime('%Y-%m-%d'),
            'time': self.departure_time.strftime('%H:%M'),
            'formatted_date': self.departure_date.strftime('%A, %B %d, %Y'),
            'formatted_time': self.departure_time.strftime('%I:%M %p')
        }


class Stop(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    is_pickup = models.BooleanField(default=True, help_text="Is this a pickup point?")
    is_dropoff = models.BooleanField(default=True, help_text="Is this a drop-off point?")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['bus', 'stop_name', 'location']
        ordering = ['stop_name', 'location']
        verbose_name = 'Stop'
        verbose_name_plural = 'Stops'
    
    def __str__(self):
        stop_type = []
        if self.is_pickup:
            stop_type.append("Pickup")
        if self.is_dropoff:
            stop_type.append("Drop-off")
        return f"{self.bus.bus_no}: {self.stop_name} ({', '.join(stop_type)})"
    
    @property
    def display_name(self):
        return f"{self.stop_name} - {self.location}"


def get_default_time():
    return timezone.now().time()

class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    trip_date = models.DateField(default=timezone.now)  # The actual date when the trip happens
    departure_time = models.TimeField(default=get_default_time)  # Actual departure time for this booking
    from_location = models.CharField(max_length=100, default="")
    to_location = models.CharField(max_length=100, default="")
    is_return_trip = models.BooleanField(default=True)
    selected_stop = models.ForeignKey('Stop', null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings_selected')
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        unique_together = ['student', 'bus']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
    
    def __str__(self):
        stop_str = f" → {self.selected_stop.location}" if self.selected_stop else ""
        return f"{self.student.full_name} - {self.bus.bus_no}{stop_str}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.send_confirmation_email()
    
    def send_confirmation_email(self):
        subject = f'Booking Confirmation - {self.bus.route_name}'
        stop_str = f" → {self.selected_stop.location}" if self.selected_stop else ""
        message = f"""
        Dear {self.student.full_name},
        
        Your booking has been confirmed!
        
        Booking Details:
        - Bus Number: {self.bus.bus_no}
        - Route: {self.bus.route_name}
        - From: {self.from_location or self.bus.from_location}{stop_str}
        - To: {self.to_location or self.bus.to_location}
        - Departure Time: {self.bus.departure_time}
        - Trip Date: {self.trip_date.strftime('%Y-%m-%d')}
        - Booking Date: {self.booking_date.strftime('%Y-%m-%d %H:%M')}
        
        Please arrive at the pickup point 10 minutes before departure time.
        
        Thank you!
        College Transport Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.student.email],
            fail_silently=False,
        )


class BookingOTP(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='otp')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Booking OTP'
        verbose_name_plural = 'Booking OTPs'

    def __str__(self):
        return f"OTP for Booking {self.booking.id} - Verified: {self.verified}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def regenerate_otp(self):
        """Regenerate OTP for expired OTPs"""
        import random
        import string
        from datetime import timedelta
        
        # Generate new 6-digit OTP
        self.otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Set new expiration time (15 minutes from now)
        self.expires_at = timezone.now() + timedelta(minutes=15)
        
        # Reset verification status
        self.verified = False
        
        # Save the changes
        self.save()
        
        # Send new OTP email
        self.send_otp_email()
        
        return self.otp_code
    
    def send_otp_email(self):
        """Send OTP email to the student"""
        subject = f'New OTP for Booking - {self.booking.bus.route_name}'
        message = f"""
        Dear {self.booking.student.full_name},
        
        A new OTP has been generated for your booking.
        
        Booking Details:
        - Bus Number: {self.booking.bus.bus_no}
        - Route: {self.booking.bus.route_name}
        - Trip Date: {self.booking.trip_date.strftime('%Y-%m-%d')}
        - Departure Time: {self.booking.departure_time}
        
        Your new OTP: {self.otp_code}
        Expires at: {self.expires_at.strftime('%Y-%m-%d %H:%M')}
        
        Please use this OTP to verify your booking.
        
        Thank you!
        College Transport Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.booking.student.email],
            fail_silently=False,
        )


class SiteConfiguration(models.Model):
    allowed_years = models.JSONField(default=list, help_text="List of allowed student years for login, e.g. ['2', '3', '4']")
    booking_open = models.BooleanField(default=True, help_text="If disabled, students cannot create new bookings")

    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'

    def __str__(self):
        return "Site Configuration"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj