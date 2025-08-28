from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.current_user, name='current_user'),
    path('buses/', views.BusListView.as_view(), name='bus_list'),
    path('bookings/', views.BookingCreateView.as_view(), name='booking_create'),
    path('bookings/current/', views.current_booking, name='current_booking'),
    path('bookings/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/verify-otp/', views.verify_booking_otp, name='verify_booking_otp'),
    path('debug-request/', views.debug_request, name='debug_request'),
    path('test-booking-data/', views.test_booking_data, name='test_booking_data'),
]