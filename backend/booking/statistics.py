from django.utils import timezone
from datetime import timedelta
from .models import Student, Bus, Booking
from django.db.models import Count, Q, Avg
from django.db import models
from dataclasses import dataclass
from typing import List, Dict, Any
import math


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


@dataclass
class RouteDemand:
    route_name: str
    date: str
    total_confirmed: int
    capacity_per_bus: int
    required_buses: int


def compute_route_demands(target_date=None) -> List[RouteDemand]:
    if target_date is None:
        target_date = timezone.now().date()
    buses = Bus.objects.filter(departure_date=target_date)
    routes = {}
    for bus in buses:
        key = (bus.route_name, target_date)
        if key not in routes:
            routes[key] = {
                'capacity': bus.capacity,
                'total': 0,
            }
        # Sum confirmed bookings across buses for this route/date
        count = Booking.objects.filter(bus__route_name=bus.route_name, trip_date=target_date, status='confirmed').count()
        routes[key]['total'] = count
        routes[key]['capacity'] = bus.capacity  # assume uniform capacity per route
    results: List[RouteDemand] = []
    for (route_name, d), vals in routes.items():
        capacity = max(1, vals['capacity'])
        total = vals['total']
        required = max(1, math.ceil(total / capacity))
        results.append(RouteDemand(route_name, d.strftime('%Y-%m-%d'), total, capacity, required))
    return results
