from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Student, Bus, Booking, Stop, SiteConfiguration


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 
                 'year', 'roll_no', 'dept', 'gender']


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'stop_name', 'location', 'is_pickup', 'is_dropoff', 'is_active', 'display_name']


class BusSerializer(serializers.ModelSerializer):
    available_seats = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    route_display = serializers.ReadOnlyField()
    stops = StopSerializer(many=True, read_only=True)
    
    class Meta:
        model = Bus
        fields = ['id', 'bus_no', 'route_name', 'from_location', 'to_location', 
                 'route_display', 'departure_date', 'departure_time', 
                 'capacity', 'available_seats', 'is_full', 'stops', 'is_booking_open']


class BookingSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    bus = BusSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    selected_stop = StopSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'student', 'bus', 'booking_date', 'trip_date', 'departure_time', 'from_location', 'to_location', 'selected_stop', 'status']


class CreateBookingSerializer(serializers.Serializer):
    bus_id = serializers.IntegerField()
    trip_date = serializers.DateField()
    departure_time = serializers.TimeField()
    from_location = serializers.CharField(max_length=100, allow_blank=True, default='')
    to_location = serializers.CharField(max_length=100, allow_blank=True, default='')
    selected_stop_id = serializers.IntegerField(required=True)
    
    def validate_trip_date(self, value):
        from datetime import date
        
        # Convert value to date if it's a string
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError as e:
                raise serializers.ValidationError(f"Invalid date format: {e}")
        
        if value < date.today():
            raise serializers.ValidationError("Trip date must be today or in the future")
        
        return value
    
    def validate_departure_time(self, value):
        return value
    
    def validate_bus_id(self, value):
        try:
            bus = Bus.objects.get(id=value)
            
            if bus.is_full:
                raise serializers.ValidationError("Bus is full")
            
            return value
        except Bus.DoesNotExist:
            raise serializers.ValidationError("Bus not found")
        except Exception as e:
            raise serializers.ValidationError(f"Error validating bus: {str(e)}")
    
    def validate(self, data):
        user = self.context['request'].user
        
        try:
            has_booking = user.has_active_booking()
            
            if has_booking:
                raise serializers.ValidationError("You already have an active booking")
            
            return data
        except Exception as e:
            raise serializers.ValidationError(f"Validation error: {str(e)}")


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
                    # Check allowed years from SiteConfiguration
                    config = SiteConfiguration.get_solo()
                    allowed_years = config.allowed_years if config else ['2', '3', '4']
                    # Accept both string and int for year comparison
                    allowed_years_str = set(str(y) for y in allowed_years)
                    if str(user.year) not in allowed_years_str:
                        raise serializers.ValidationError("Login is not allowed for your year.")
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError("User account is disabled")
            else:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Email and password are required")