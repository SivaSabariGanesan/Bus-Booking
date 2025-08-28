from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from datetime import timedelta
from .models import Student, Bus, Booking


class DepartureDateFilter(admin.SimpleListFilter):
    title = 'Departure Date'
    parameter_name = 'departure_date_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('tomorrow', 'Tomorrow'),
            ('this_week', 'This Week'),
            ('next_week', 'Next Week'),
            ('past', 'Past Dates'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        
        if self.value() == 'today':
            return queryset.filter(departure_date=today)
        elif self.value() == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            return queryset.filter(departure_date=tomorrow)
        elif self.value() == 'this_week':
            end_of_week = today + timedelta(days=6)
            return queryset.filter(departure_date__range=[today, end_of_week])
        elif self.value() == 'next_week':
            start_next_week = today + timedelta(days=7)
            end_next_week = start_next_week + timedelta(days=6)
            return queryset.filter(departure_date__range=[start_next_week, end_next_week])
        elif self.value() == 'past':
            return queryset.filter(departure_date__lt=today)
        
        return queryset


class BusAdminForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = '__all__'

@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'roll_no', 'dept', 'year', 'is_active')
    list_filter = ('year', 'dept', 'gender', 'student_type', 'degree_type', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'roll_no')
    ordering = ('email',)
    filter_horizontal = ()
    readonly_fields = ('last_login', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'gender')
        }),
        ('Academic info', {
            'fields': ('roll_no', 'dept', 'year', 'student_type', 'degree_type')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 
                      'phone_number', 'roll_no', 'dept', 'year', 'gender', 
                      'student_type', 'degree_type'),
        }),
    )


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    form = BusAdminForm
    list_display = ('bus_no', 'route_name', 'from_location', 'to_location', 'departure_date', 'departure_time', 'capacity', 'available_seats')
    list_filter = (DepartureDateFilter, 'route_name', 'from_location', 'to_location')
    search_fields = ('bus_no', 'route_name', 'from_location', 'to_location')
    ordering = ('bus_no',)
    actions = ['set_today_departure', 'set_tomorrow_departure', 'set_next_week_departure']
    readonly_fields = ('departure_info_display',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('bus_no', 'route_name', 'from_location', 'to_location')
        }),
        ('Schedule', {
            'fields': ('departure_date', 'departure_time', 'departure_info_display')
        }),
        ('Capacity', {
            'fields': ('capacity',)
        }),
    )
    
    def departure_info_display(self, obj):
        """Display formatted departure information"""
        if obj.departure_date and obj.departure_time:
            return f"<strong>{obj.departure_date.strftime('%A, %B %d, %Y')} at {obj.departure_time.strftime('%I:%M %p')}</strong>"
        return "Not set"
    departure_info_display.short_description = "Departure Details"
    departure_info_display.allow_tags = True
    
    def set_today_departure(self, request, queryset):
        """Set selected buses to depart today"""
        today = timezone.now().date()
        updated = queryset.update(departure_date=today)
        self.message_user(request, f'{updated} buses updated to depart today ({today})')
    set_today_departure.short_description = "Set buses to depart today"
    
    def set_tomorrow_departure(self, request, queryset):
        """Set selected buses to depart tomorrow"""
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        updated = queryset.update(departure_date=tomorrow)
        self.message_user(request, f'{updated} buses updated to depart tomorrow ({tomorrow})')
    set_tomorrow_departure.short_description = "Set buses to depart tomorrow"
    
    def set_next_week_departure(self, request, queryset):
        """Set selected buses to depart next week (Monday)"""
        today = timezone.now().date()
        days_until_monday = (7 - today.weekday()) % 7
        next_monday = today + timedelta(days=days_until_monday)
        updated = queryset.update(departure_date=next_monday)
        self.message_user(request, f'{updated} buses updated to depart next Monday ({next_monday})')
    set_next_week_departure.short_description = "Set buses to depart next Monday"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'bus', 'booking_date', 'trip_date', 'departure_time', 'from_location', 'to_location', 'status', 'otp_code')
    list_filter = ('bus__route_name', 'trip_date', 'departure_time', 'booking_date', 'status')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'bus__bus_no', 'from_location', 'to_location')
    ordering = ('-booking_date',)
    
    fieldsets = (
        ('Basic Info', {'fields': ('student', 'bus')}),
        ('Trip Details', {'fields': ('trip_date', 'departure_time', 'from_location', 'to_location')}),
        ('System Info', {'fields': ('booking_date',)}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('booking_date',)
        return ()

    def otp_code(self, obj):
        if hasattr(obj, 'otp') and obj.otp:
            return obj.otp.otp_code
        return '-'
    otp_code.short_description = 'OTP Code'