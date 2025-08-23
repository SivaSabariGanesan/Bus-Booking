from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Student, Bus, Booking


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 
                 'year', 'roll_no', 'dept', 'gender', 'student_type', 'degree_type']


class BusSerializer(serializers.ModelSerializer):
    available_seats = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Bus
        fields = ['id', 'bus_no', 'route_name', 'departure_time', 'return_time', 
                 'capacity', 'available_seats', 'is_full']


class BookingSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    bus = BusSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'student', 'bus', 'booking_date', 'is_return_trip', 'trip_type', 'from_location', 'to_location']


class CreateBookingSerializer(serializers.Serializer):
    bus_id = serializers.IntegerField()
    trip_type = serializers.ChoiceField(choices=[('RETURN', 'Return Trip'), ('WEEKEND', 'Weekend Trip')], default='RETURN')
    trip_date = serializers.DateField()
    departure_time = serializers.TimeField()
    return_time = serializers.TimeField(required=False, allow_null=True)
    from_location = serializers.CharField(max_length=100, allow_blank=True, default='')
    to_location = serializers.CharField(max_length=100, allow_blank=True, default='')
    
    def validate_trip_date(self, value):
        from datetime import date, timedelta
        today = date.today()
        
        if value <= today:
            raise serializers.ValidationError("Trip date must be in the future")
        
        # For weekend trips, ensure it's on a weekend (Saturday or Sunday)
        if self.initial_data.get('trip_type') == 'WEEKEND':
            if value.weekday() not in [5, 6]:  # 5=Saturday, 6=Sunday
                raise serializers.ValidationError("Weekend trips must be on Saturday or Sunday")
        
        return value
    
    def validate_bus_id(self, value):
        try:
            bus = Bus.objects.get(id=value)
            if bus.is_full():
                raise serializers.ValidationError("Bus is full")
            return value
        except Bus.DoesNotExist:
            raise serializers.ValidationError("Bus not found")
    
    def validate(self, data):
        user = self.context['request'].user
        if user.has_active_booking():
            raise serializers.ValidationError("You already have an active booking")
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError("User account is disabled")
            else:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Email and password are required")