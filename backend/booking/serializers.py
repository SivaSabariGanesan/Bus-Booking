from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Student, Bus, Booking, Stop


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 
                 'year', 'roll_no', 'dept', 'gender', 'student_type', 'degree_type']


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
                 'capacity', 'available_seats', 'is_full', 'stops']


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
        print(f"=== VALIDATING TRIP DATE ===")
        print(f"Input value: {value}")
        print(f"Input type: {type(value)}")
        print(f"Input repr: {repr(value)}")
        
        from datetime import date, timedelta
        today = date.today()
        print(f"Today's date: {today}")
        print(f"Today's type: {type(today)}")
        
        # Convert value to date if it's a string
        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
                print(f"Converted string to date: {value}")
            except ValueError as e:
                print(f"Failed to parse date string: {e}")
                raise serializers.ValidationError(f"Invalid date format: {e}")
        
        print(f"Final value to compare: {value}")
        print(f"Final value type: {type(value)}")
        
        if value < today:
            print(f"Trip date {value} is not today or in the future")
            raise serializers.ValidationError("Trip date must be today or in the future")
        
        print(f"Trip date {value} is valid")
        return value
    
    def validate_departure_time(self, value):
        print(f"Validating departure_time: {value} (type: {type(value)})")  # Debug log
        return value
    
    def validate_bus_id(self, value):
        print(f"=== VALIDATING BUS ID ===")
        print(f"Input value: {value}")
        print(f"Input type: {type(value)}")
        
        try:
            bus = Bus.objects.get(id=value)
            print(f"Found bus: {bus.bus_no}")
            print(f"Bus capacity: {bus.capacity}")
            print(f"Bus bookings count: {bus.booking_set.count()}")
            
            if bus.is_full:
                print(f"Bus {bus.bus_no} is full")
                raise serializers.ValidationError("Bus is full")
            
            print(f"Bus {bus.bus_no} has available seats")
            return value
        except Bus.DoesNotExist:
            print(f"Bus with id {value} not found")
            raise serializers.ValidationError("Bus not found")
        except Exception as e:
            print(f"Unexpected error validating bus_id: {e}")
            raise serializers.ValidationError(f"Error validating bus: {str(e)}")
    
    def validate(self, data):
        print(f"=== FINAL VALIDATION ===")
        print(f"Complete data: {data}")
        print(f"Data type: {type(data)}")
        
        user = self.context['request'].user
        print(f"User: {user.email}")
        print(f"User type: {type(user)}")
        
        try:
            has_booking = user.has_active_booking()
            print(f"User has active booking: {has_booking}")
            
            if has_booking:
                print(f"User {user.email} already has an active booking")
                raise serializers.ValidationError("You already have an active booking")
            
            print(f"User {user.email} validation passed")
            return data
        except Exception as e:
            print(f"Error in final validation: {e}")
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
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError("User account is disabled")
            else:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Email and password are required")