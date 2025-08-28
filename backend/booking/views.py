from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import Student, Bus, Booking, BookingOTP
from .serializers import (
    StudentSerializer, BusSerializer, BookingSerializer, 
    CreateBookingSerializer, LoginSerializer
)
from django.views.decorators.csrf import csrf_exempt
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        return Response({
            'success': True,
            'user': StudentSerializer(user).data
        })
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response(StudentSerializer(request.user).data)


class BusListView(generics.ListAPIView):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter buses by departure date if specified"""
        queryset = Bus.objects.all()
        
        # Filter by departure date if provided
        departure_date = self.request.query_params.get('departure_date', None)
        if departure_date:
            try:
                from datetime import datetime
                target_date = datetime.strptime(departure_date, '%Y-%m-%d').date()
                queryset = queryset.filter(departure_date=target_date)
            except ValueError:
                # If date format is invalid, return all buses
                pass
        
        # Filter by from_location if provided
        from_location = self.request.query_params.get('from_location', None)
        if from_location:
            queryset = queryset.filter(from_location__icontains=from_location)
        
        # Filter by to_location if provided
        to_location = self.request.query_params.get('to_location', None)
        if to_location:
            queryset = queryset.filter(to_location__icontains=to_location)
        
        return queryset.order_by('departure_date', 'departure_time')


@api_view(['POST'])
def debug_request(request):
    """Debug endpoint to see raw request data"""
    try:
        print("=== DEBUG REQUEST ===")
        print(f"Request method: {request.method}")
        print(f"Content type: {request.content_type}")
        print(f"Request data: {request.data}")
        
        return Response({
            'success': True,
            'method': request.method,
            'content_type': request.content_type,
            'data': request.data,
        })
    except Exception as e:
        print(f"Error in debug endpoint: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def test_booking_data(request):
    """Test endpoint to see what data is being received"""
    print("=== TEST BOOKING DATA ===")
    print(f"Request data: {request.data}")
    print(f"Request data type: {type(request.data)}")
    print(f"Content type: {request.content_type}")
    
    # Try to parse the data
    try:
        bus_id = request.data.get('bus_id')
        trip_date = request.data.get('trip_date')
        departure_time = request.data.get('departure_time')
        from_location = request.data.get('from_location')
        to_location = request.data.get('to_location')
        
        print(f"Parsed data:")
        print(f"  bus_id: {bus_id} (type: {type(bus_id)})")
        print(f"  trip_date: {trip_date} (type: {type(trip_date)})")
        print(f"  departure_time: {departure_time} (type: {type(departure_time)})")
        print(f"  from_location: {from_location} (type: {type(from_location)})")
        print(f"  to_location: {to_location} (type: {type(to_location)})")
        
        return Response({
            'success': True,
            'received_data': request.data,
            'parsed_data': {
                'bus_id': bus_id,
                'trip_date': trip_date,
                'departure_time': departure_time,
                'from_location': from_location,
                'to_location': to_location
            }
        })
        
    except Exception as e:
        print(f"Error parsing data: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'received_data': request.data
        }, status=400)


class BookingCreateView(generics.CreateAPIView):
    serializer_class = CreateBookingSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        print(f"=== BOOKING CREATE VIEW ===")
        print(f"Request method: {request.method}")
        print(f"Request user: {request.user.email}")
        print(f"Request data: {request.data}")
        print(f"Request data type: {type(request.data)}")
        serializer = self.get_serializer(data=request.data)
        print(f"Serializer created: {serializer}")
        print("=== CALLING SERIALIZER VALIDATION ===")
        is_valid = serializer.is_valid()
        print(f"Serializer is_valid result: {is_valid}")
        if not is_valid:
            print(f"Validation errors: {serializer.errors}")
            print(f"Validation errors type: {type(serializer.errors)}")
            return Response({
                'success': False,
                'errors': serializer.errors,
                'received_data': request.data  # Include received data for debugging
            }, status=status.HTTP_400_BAD_REQUEST)
        print("=== SERIALIZER VALIDATION PASSED ===")
        print(f"Validated data: {serializer.validated_data}")
        try:
            bus = Bus.objects.get(id=serializer.validated_data['bus_id'])
            print(f"Found bus: {bus.bus_no}")  # Debug log
            # Create booking as pending
            booking = Booking.objects.create(
                student=request.user,
                bus=bus,
                trip_date=serializer.validated_data['trip_date'],
                departure_time=serializer.validated_data['departure_time'],
                from_location=serializer.validated_data['from_location'],
                to_location=serializer.validated_data['to_location'],
                status='pending',
            )
            # Generate OTP
            otp_code = str(random.randint(100000, 999999))
            expires_at = timezone.now() + timedelta(minutes=10)
            BookingOTP.objects.create(
                booking=booking,
                otp_code=otp_code,
                expires_at=expires_at,
            )
            # Send OTP email
            subject = 'Your Bus Booking OTP'
            message = f"Your OTP for confirming your bus booking is: {otp_code}\nThis OTP is valid for 10 minutes."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
            print(f"OTP {otp_code} sent to {request.user.email}")
            return Response({
                'success': True,
                'otp_sent': True,
                'pending_booking_id': booking.id
            }, status=status.HTTP_201_CREATED)
        except Bus.DoesNotExist:
            print(f"Bus not found: {serializer.validated_data['bus_id']}")  # Debug log
            return Response({
                'success': False,
                'errors': {'bus_id': ['Bus not found']}
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error creating booking: {str(e)}")  # Debug log
            return Response({
                'success': False,
                'errors': {'non_field_errors': [f'Error creating booking: {str(e)}']}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_booking(request):
    try:
        booking = Booking.objects.filter(student=request.user, status__in=['pending', 'confirmed']).order_by('-booking_date').first()
        if booking:
            return Response(BookingSerializer(booking).data)
        else:
            return Response({'booking': None})
    except Exception as e:
        return Response({'booking': None, 'error': str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_booking(request):
    try:
        booking = Booking.objects.get(student=request.user)
        booking.delete()
        return Response({'success': True, 'message': 'Booking cancelled successfully'})
    except Booking.DoesNotExist:
        return Response({
            'success': False, 
            'message': 'No active booking found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def verify_booking_otp(request):
    booking_id = request.data.get('pending_booking_id')
    otp = request.data.get('otp')
    if not booking_id or not otp:
        return Response({'success': False, 'error': 'Missing booking ID or OTP'}, status=400)
    try:
        booking = Booking.objects.get(id=booking_id, status='pending')
        booking_otp = booking.otp
        if booking_otp.verified:
            return Response({'success': False, 'error': 'OTP already used'}, status=400)
        if timezone.now() > booking_otp.expires_at:
            return Response({'success': False, 'error': 'OTP expired'}, status=400)
        if booking_otp.otp_code != otp:
            return Response({'success': False, 'error': 'Invalid OTP'}, status=400)
        # Mark OTP as verified and booking as confirmed
        booking_otp.verified = True
        booking_otp.save()
        booking.status = 'confirmed'
        booking.save()
        # Send confirmation email
        booking.send_confirmation_email()
        return Response({'success': True, 'message': 'Booking confirmed'})
    except Booking.DoesNotExist:
        return Response({'success': False, 'error': 'Pending booking not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)