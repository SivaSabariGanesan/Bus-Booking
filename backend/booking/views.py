from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .models import Student, Bus, Booking
from .serializers import (
    StudentSerializer, BusSerializer, BookingSerializer, 
    CreateBookingSerializer, LoginSerializer
)
from django.views.decorators.csrf import csrf_exempt


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


class BookingCreateView(generics.CreateAPIView):
    serializer_class = CreateBookingSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        print(f"Received booking data: {request.data}")  # Debug log
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")  # Debug log
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        bus = Bus.objects.get(id=serializer.validated_data['bus_id'])
        booking = Booking.objects.create(
            student=request.user,
            bus=bus,
            trip_date=serializer.validated_data['trip_date'],
            departure_time=serializer.validated_data['departure_time'],
            return_time=serializer.validated_data.get('return_time'),
            is_return_trip=(serializer.validated_data['trip_type'] == 'RETURN'),
            trip_type=serializer.validated_data['trip_type'],
            from_location=serializer.validated_data['from_location'],
            to_location=serializer.validated_data['to_location'],
        )
        
        return Response({
            'success': True,
            'booking': BookingSerializer(booking).data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_booking(request):
    try:
        booking = Booking.objects.get(student=request.user)
        return Response(BookingSerializer(booking).data)
    except Booking.DoesNotExist:
        return Response({'booking': None})


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