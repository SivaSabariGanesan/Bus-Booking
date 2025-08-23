from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.current_user, name='current_user'),
    path('buses/', views.BusListView.as_view(), name='bus_list'),
    path('bookings/', views.BookingCreateView.as_view(), name='create_booking'),
    path('bookings/current/', views.current_booking, name='current_booking'),
    path('bookings/cancel/', views.cancel_booking, name='cancel_booking'),
]