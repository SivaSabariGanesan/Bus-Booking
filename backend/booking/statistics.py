from django.utils import timezone
from datetime import timedelta
from .models import Student, Bus, Booking
from django.db.models import Count, Q, Avg
from django.db import models


class StatisticsDashboard:
    """Simple statistics dashboard accessible from admin"""
    
    @staticmethod
    def get_quick_stats():
        """Get quick statistics for admin dashboard"""
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        
        stats = {
            'total_students': Student.objects.count(),
            'total_buses': Bus.objects.count(),
            'total_bookings': Booking.objects.count(),
            'active_bookings': Booking.objects.filter(status__in=['pending', 'confirmed']).count(),
            'recent_bookings': Booking.objects.filter(booking_date__gte=last_week).count(),
            'pending_bookings': Booking.objects.filter(status='pending').count(),
            'confirmed_bookings': Booking.objects.filter(status='confirmed').count(),
        }
        
        return stats
    
    @staticmethod
    def get_detailed_stats():
        """Get detailed statistics for admin dashboard"""
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        # Department statistics
        dept_stats = Student.objects.values('dept').annotate(
            total=Count('id'),
            with_bookings=Count('id', filter=Q(booking__status__in=['pending', 'confirmed']))
        ).order_by('-total')
        
        # Year-wise statistics
        year_stats = Student.objects.values('year').annotate(
            total=Count('id'),
            with_bookings=Count('id', filter=Q(booking__status__in=['pending', 'confirmed']))
        ).order_by('year')
        
        # Bus utilization
        bus_utilization = Bus.objects.annotate(
            booking_count=Count('booking'),
            utilization_percent=Count('booking') * 100.0 / models.F('capacity')
        ).values('bus_no', 'route_name', 'capacity', 'booking_count', 'utilization_percent')
        
        # Route popularity
        route_stats = Bus.objects.values('route_name').annotate(
            total_bookings=Count('booking'),
            avg_utilization=Avg(Count('booking') * 100.0 / models.F('capacity'))
        ).order_by('-total_bookings')
        
        return {
            'dept_stats': list(dept_stats),
            'year_stats': list(year_stats),
            'bus_utilization': list(bus_utilization),
            'route_stats': list(route_stats),
        }
