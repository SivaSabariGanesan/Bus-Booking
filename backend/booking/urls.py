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
    path('bookings/resend-otp/', views.resend_otp, name='resend_otp'),
    
    # Admin URLs for pickup and drop-off management
    path('admin/pickup-list/', views.admin_pickup_list, name='admin_pickup_list'),
    path('admin/dropoff-list/', views.admin_dropoff_list, name='admin_dropoff_list'),
    path('admin/export-pickup-list/', views.admin_export_pickup_list, name='admin_export_pickup_list'),
    path('admin/export-dropoff-list/', views.admin_export_dropoff_list, name='admin_export_dropoff_list'),
]