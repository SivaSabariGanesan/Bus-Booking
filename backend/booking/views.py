from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import Student, Bus, Booking, BookingOTP, SiteConfiguration
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
from django.http import HttpResponse
import csv
from .models import PasswordResetOTP


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
        """Filter buses based on student's booking status and 24-hour restriction"""
        user = self.request.user
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
        
        # Apply 24-hour restriction logic
        # Use the same buses for both directions - system determines direction based on student status
        if user.should_book_return_trip():
            # Student should book return trip - show all buses but display as TO REC
            # The frontend will display these as "Destination → REC College" for return trips
            queryset = queryset.all()
        elif user.has_outbound_booking():
            # Student has active outbound booking but not ready for return yet
            # Show all buses but display as FROM REC
            # The frontend will display these as "REC College → Destination" for outbound trips
            queryset = queryset.all()
        else:
            # Student has no outbound booking - show all buses as FROM REC
            # The frontend will display these as "REC College → Destination" for outbound trips
            queryset = queryset.all()
        
        # Additional filters
        from_location = self.request.query_params.get('from_location', None)
        if from_location:
            queryset = queryset.filter(from_location__icontains=from_location)
        
        to_location = self.request.query_params.get('to_location', None)
        if to_location:
            queryset = queryset.filter(to_location__icontains=to_location)
        
        return queryset.order_by('departure_date', 'departure_time')


@api_view(['POST'])
def debug_request(request):
    """Debug endpoint to see raw request data"""
    try:
        return Response({
            'success': True,
            'method': request.method,
            'content_type': request.content_type,
            'data': request.data,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def test_booking_data(request):
    """Test endpoint for booking data validation"""
    try:
        return Response({
            'success': True,
            'data': request.data,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


class BookingCreateView(generics.CreateAPIView):
    serializer_class = CreateBookingSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        print(f"=== BOOKING CREATE VIEW ===")
        # Check if booking is open
        try:
            config = SiteConfiguration.get_solo()
            if not config.booking_open:
                return Response({
                    'success': False,
                    'errors': {'non_field_errors': ['Booking is currently closed. Please try again later.']}
                }, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            pass
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
            # Enforce per-bus booking open/close
            if not getattr(bus, 'is_booking_open', True):
                return Response({
                    'success': False,
                    'errors': {'non_field_errors': ['Booking for this bus is currently closed.']}
                }, status=status.HTTP_403_FORBIDDEN)
            print(f"Found bus: {bus.bus_no}")  # Debug log
            # Determine locations based on trip type
            is_outbound_trip = serializer.validated_data.get('is_outbound_trip', True)
            
            if is_outbound_trip:
                # For FROM REC trips, use bus locations as is
                from_location = bus.from_location
                to_location = bus.to_location
            else:
                # For TO REC trips, reverse the locations to show "Destination → REC College"
                from_location = bus.to_location  # Destination becomes pickup
                to_location = bus.from_location  # REC becomes dropoff
            
            # Get selected stop
            selected_stop_id = serializer.validated_data.get('selected_stop_id')
            selected_stop = None
            if selected_stop_id:
                try:
                    selected_stop = bus.stops.get(id=selected_stop_id)
                except Exception as e:
                    print(f"Error finding selected stop: {e}")
            
            # Set 24-hour restriction fields
            outbound_booking_date = None
            return_trip_available_after = None
            
            if is_outbound_trip:
                outbound_booking_date = timezone.now()
                return_trip_available_after = timezone.now() + timedelta(hours=24)
            
            print(f"Creating {'outbound' if is_outbound_trip else 'return'} booking:")
            print(f"  - From: {from_location}")
            print(f"  - To: {to_location}")
            print(f"  - Bus: {bus.bus_no}")
            print(f"  - Trip Type: {'FROM REC' if is_outbound_trip else 'TO REC'}")
            
            booking = Booking.objects.create(
                student=request.user,
                bus=bus,
                trip_date=serializer.validated_data['trip_date'],
                departure_time=serializer.validated_data['departure_time'],
                from_location=from_location,
                to_location=to_location,
                selected_stop=selected_stop,
                status='pending',
                is_outbound_trip=is_outbound_trip,
                outbound_booking_date=outbound_booking_date,
                return_trip_available_after=return_trip_available_after,
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
            return Response({'booking': BookingSerializer(booking).data})
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
@permission_classes([IsAuthenticated])
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_otp(request):
    """Resend OTP for expired bookings"""
    booking_id = request.data.get('booking_id')
    if not booking_id:
        return Response({'success': False, 'error': 'Missing booking ID'}, status=400)
    
    try:
        # First check if booking exists for this user
        booking = Booking.objects.get(id=booking_id, student=request.user, status='pending')
        
        # Check if booking has an OTP
        try:
            booking_otp = booking.otp
        except BookingOTP.DoesNotExist:
            # Create new OTP if none exists
            otp_code = str(random.randint(100000, 999999))
            expires_at = timezone.now() + timedelta(minutes=15)
            booking_otp = BookingOTP.objects.create(
                booking=booking,
                otp_code=otp_code,
                expires_at=expires_at,
            )
        
        # Check if OTP is expired - production security
        if not booking_otp.is_expired():
            return Response({
                'success': False, 
                'error': 'OTP is still valid. Please use the existing OTP.'
            }, status=400)
        
        # Regenerate OTP
        new_otp = booking_otp.regenerate_otp()
        
        return Response({
            'success': True, 
            'message': 'New OTP sent successfully'
        })
        
    except Booking.DoesNotExist:
        return Response({
            'success': False, 
            'error': 'Booking not found or you do not have permission to access it'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False, 
            'error': 'Failed to resend OTP. Please try again later.'
        }, status=500)


# Admin Views for Pickup and Drop-off Management

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_pickup_list(request):
    """Get list of all pickup bookings for a specific date"""
    try:
        # Check if user is admin/staff
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        date = request.GET.get('date')
        if not date:
            return Response({
                'success': False,
                'error': 'Date parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all outbound bookings (FROM REC) for the specified date
        pickups = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=True,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        pickup_data = []
        for pickup in pickups:
            pickup_data.append({
                'id': pickup.id,
                'student_name': pickup.student.full_name,
                'student_roll_no': pickup.student.roll_no,
                'student_dept': pickup.student.dept,
                'student_phone': pickup.student.phone_number,
                'pickup_location': pickup.from_location,
                'destination': pickup.to_location,
                'departure_time': pickup.departure_time.strftime('%H:%M'),
                'bus_number': pickup.bus.bus_no,
                'route_name': pickup.bus.route_name,
                'status': pickup.status,
                'booking_date': pickup.booking_date.strftime('%Y-%m-%d %H:%M')
            })
        
        return Response({
            'success': True,
            'date': date,
            'pickup_count': len(pickup_data),
            'pickups': pickup_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error fetching pickup list: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dropoff_list(request):
    """Get list of all drop-off bookings for a specific date"""
    try:
        # Check if user is admin/staff
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        date = request.GET.get('date')
        if not date:
            return Response({
                'success': False,
                'error': 'Date parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all return bookings (TO REC) for the specified date
        dropoffs = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=False,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        dropoff_data = []
        for dropoff in dropoffs:
            dropoff_data.append({
                'id': dropoff.id,
                'student_name': dropoff.student.full_name,
                'student_roll_no': dropoff.student.roll_no,
                'student_dept': dropoff.student.dept,
                'student_phone': dropoff.student.phone_number,
                'pickup_location': dropoff.from_location,
                'dropoff_location': dropoff.to_location,
                'departure_time': dropoff.departure_time.strftime('%H:%M'),
                'bus_number': dropoff.bus.bus_no,
                'route_name': dropoff.bus.route_name,
                'status': dropoff.status,
                'booking_date': dropoff.booking_date.strftime('%Y-%m-%d %H:%M')
            })
        
        return Response({
            'success': True,
            'date': date,
            'dropoff_count': len(dropoff_data),
            'dropoffs': dropoff_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error fetching drop-off list: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_export_pickup_list(request):
    """Export pickup list to CSV for a specific date"""
    try:
        # Check if user is admin/staff
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        date = request.GET.get('date')
        if not date:
            return Response({
                'success': False,
                'error': 'Date parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all outbound bookings (FROM REC) for the specified date
        pickups = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=True,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="pickup_list_{date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Student Name', 'Roll No', 'Department', 'Phone', 
            'Pickup Location', 'Destination', 'Departure Time', 
            'Bus Number', 'Route Name', 'Status', 'Booking Date'
        ])
        
        for pickup in pickups:
            writer.writerow([
                pickup.student.full_name,
                pickup.student.roll_no,
                pickup.student.dept,
                pickup.student.phone_number,
                pickup.from_location,
                pickup.to_location,
                pickup.departure_time.strftime('%H:%M'),
                pickup.bus.bus_no,
                pickup.bus.route_name,
                pickup.status,
                pickup.booking_date.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error exporting pickup list: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_export_dropoff_list(request):
    """Export drop-off list to CSV for a specific date"""
    try:
        # Check if user is admin/staff
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        date = request.GET.get('date')
        if not date:
            return Response({
                'success': False,
                'error': 'Date parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all return bookings (TO REC) for the specified date
        dropoffs = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=False,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="dropoff_list_{date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Student Name', 'Roll No', 'Department', 'Phone', 
            'Pickup Location', 'Drop-off Location', 'Departure Time', 
            'Bus Number', 'Route Name', 'Status', 'Booking Date'
        ])
        
        for dropoff in dropoffs:
            writer.writerow([
                dropoff.student.full_name,
                dropoff.student.roll_no,
                dropoff.student.dept,
                dropoff.student.phone_number,
                dropoff.from_location,
                dropoff.to_location,
                dropoff.departure_time.strftime('%H:%M'),
                dropoff.bus.bus_no,
                dropoff.bus.route_name,
                dropoff.status,
                dropoff.booking_date.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error exporting drop-off list: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Forgot Password Views
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request(request):
    """Request password reset OTP"""
    try:
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student exists
        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No account found with this email address'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if student is active
        if not student.is_active:
            return Response({
                'success': False,
                'error': 'Account is deactivated. Please contact administrator.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create password reset OTP
        try:
            otp = PasswordResetOTP.create_for_student(student)
            return Response({
                'success': True,
                'message': f'Password reset OTP has been sent to {email}',
                'expires_at': otp.expires_at.isoformat()
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to send OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_password_reset_otp(request):
    """Verify password reset OTP"""
    try:
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        
        if not email or not otp_code:
            return Response({
                'success': False,
                'error': 'Email and OTP are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student exists
        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No account found with this email address'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get the latest unused OTP for this student
        try:
            otp = PasswordResetOTP.objects.filter(
                student=student,
                used=False
            ).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No OTP found. Please request a new password reset.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify OTP
        is_valid, message = otp.verify_otp(otp_code)
        
        if is_valid:
            return Response({
                'success': True,
                'message': 'OTP verified successfully',
                'otp_id': otp.id
            })
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using verified OTP"""
    try:
        email = request.data.get('email')
        otp_id = request.data.get('otp_id')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([email, otp_id, new_password, confirm_password]):
            return Response({
                'success': False,
                'error': 'All fields are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if passwords match
        if new_password != confirm_password:
            return Response({
                'success': False,
                'error': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check password strength
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student exists
        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No account found with this email address'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get and verify OTP
        try:
            otp = PasswordResetOTP.objects.get(
                id=otp_id,
                student=student,
                verified=True,
                used=False
            )
        except PasswordResetOTP.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid or expired OTP. Please request a new password reset.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is expired
        if otp.is_expired():
            return Response({
                'success': False,
                'error': 'OTP has expired. Please request a new password reset.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        try:
            student.set_password(new_password)
            student.save()
            
            # Mark OTP as used
            otp.mark_as_used()
            
            return Response({
                'success': True,
                'message': 'Password has been reset successfully. You can now login with your new password.'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to reset password: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_password_reset_otp(request):
    """Resend password reset OTP"""
    try:
        email = request.data.get('email')
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if student exists
        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No account found with this email address'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if student is active
        if not student.is_active:
            return Response({
                'success': False,
                'error': 'Account is deactivated. Please contact administrator.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new password reset OTP
        try:
            otp = PasswordResetOTP.create_for_student(student)
            return Response({
                'success': True,
                'message': f'New password reset OTP has been sent to {email}',
                'expires_at': otp.expires_at.isoformat()
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to send OTP: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)