from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Student, Bus, Booking, Stop, SiteConfiguration
from django.utils import timezone


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
    display_direction = serializers.SerializerMethodField()
    
    class Meta:
        model = Bus
        fields = ['id', 'bus_no', 'route_name', 'from_location', 'to_location', 
                 'route_display', 'departure_date', 'departure_time', 
                 'capacity', 'available_seats', 'is_full', 'stops', 'is_booking_open', 'display_direction']
    
    def get_display_direction(self, obj):
        """Return the display direction based on student's booking status"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            if user.should_book_return_trip():
                # For return trips, show as "Destination → REC College"
                return f"{obj.to_location} → REC College"
            else:
                # For outbound trips, show as "REC College → Destination"
                return f"REC College → {obj.to_location}"
        # Default fallback
        return obj.route_display


class BookingSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    bus = BusSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    selected_stop = StopSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'student', 'bus', 'booking_date', 'trip_date', 'departure_time', 'from_location', 'to_location', 'selected_stop', 'status', 'is_outbound_trip', 'outbound_booking_date', 'return_trip_available_after']


class CreateBookingSerializer(serializers.Serializer):
    bus_id = serializers.IntegerField()
    trip_date = serializers.DateField()
    departure_time = serializers.TimeField()
    from_location = serializers.CharField(max_length=100, allow_blank=True, default='')
    to_location = serializers.CharField(max_length=100, allow_blank=True, default='')
    selected_stop_id = serializers.IntegerField(required=True)
    is_outbound_trip = serializers.BooleanField(default=True)
    
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
        bus_id = data.get('bus_id')
        is_outbound_trip = data.get('is_outbound_trip', True)
        
        try:
            bus = Bus.objects.get(id=bus_id)
            
            # Check if user already has a booking of the same type
            if is_outbound_trip and user.has_outbound_booking():
                raise serializers.ValidationError("You already have an active outbound booking")
            
            if not is_outbound_trip and user.has_return_booking():
                raise serializers.ValidationError("You already have an active return booking")
            
            # Prevent booking outbound trips if student should book return trip
            # Student should only book return trips after outbound is completed
            if is_outbound_trip and user.should_book_return_trip():
                raise serializers.ValidationError("You have completed your outbound trip. You can now only book return trips.")
            
            # For return trips, check if student should book return trip
            if not is_outbound_trip:
                if not user.should_book_return_trip():
                    # Check if student has any outbound booking history
                    has_outbound_history = user.booking_set.filter(is_outbound_trip=True).exists()
                    if not has_outbound_history:
                        raise serializers.ValidationError("You must book an outbound trip first")
                    else:
                        # Student has outbound history but not ready for return
                        availability_time = user.get_return_trip_availability_time()
                        if availability_time:
                            from datetime import timedelta
                            time_remaining = availability_time - timezone.now()
                            hours_remaining = int(time_remaining.total_seconds() / 3600)
                            minutes_remaining = int((time_remaining.total_seconds() % 3600) / 60)
                            raise serializers.ValidationError(f"Return trip available in {hours_remaining} hours and {minutes_remaining} minutes")
                        else:
                            raise serializers.ValidationError("Return trip not available yet")
            
            # Note: Same buses are used for both outbound and return trips
            # The system determines the direction based on is_outbound_trip field
            # No need to validate bus direction - all buses are available for both trip types
            
            return data
        except Bus.DoesNotExist:
            raise serializers.ValidationError("Bus not found")
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