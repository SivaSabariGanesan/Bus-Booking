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
    
    STUDENT_TYPE_CHOICES = [
        ('REGULAR', 'Regular'),
        ('LATERAL', 'Lateral Entry'),
    ]
    
    DEGREE_TYPE_CHOICES = [
        ('BTECH', 'B.Tech'),
        ('MTECH', 'M.Tech'),
        ('MBA', 'MBA'),
        ('BBA', 'BBA'),
        ('BCA', 'BCA'),
        ('MCA', 'MCA'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES)
    roll_no = models.CharField(max_length=20, unique=True)
    dept = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    student_type = models.CharField(max_length=10, choices=STUDENT_TYPE_CHOICES)
    degree_type = models.CharField(max_length=10, choices=DEGREE_TYPE_CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = StudentManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'roll_no']
    
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
        return self.booking_set.exists()


class Bus(models.Model):
    bus_no = models.CharField(max_length=20, unique=True)
    route_name = models.CharField(max_length=100)
    from_location = models.CharField(max_length=100, default="")
    to_location = models.CharField(max_length=100, default="")
    departure_date = models.DateField(default=timezone.now, help_text="Date when this bus is available for departure")
    departure_time = models.TimeField()
    capacity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.bus_no} - {self.route_name}"
    
    @property
    def available_seats(self):
        return self.capacity - self.booking_set.count()
    
    @property
    def route_display(self):
        """Display route in a user-friendly format"""
        return f"{self.from_location} → {self.to_location}"
    
    def is_full(self):
        return self.booking_set.count() >= self.capacity
    
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
    
    class Meta:
        unique_together = ['student', 'bus']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.bus.bus_no}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.send_confirmation_email()
    
    def send_confirmation_email(self):
        subject = f'Booking Confirmation - {self.bus.route_name}'
        message = f"""
        Dear {self.student.full_name},
        
        Your booking has been confirmed!
        
        Booking Details:
        - Bus Number: {self.bus.bus_no}
        - Route: {self.bus.route_name}
        - From: {self.from_location or self.bus.from_location}
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