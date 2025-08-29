from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from datetime import timedelta
from import_export.admin import ImportExportModelAdmin
from .models import Student, Bus, Booking, BookingOTP, Stop
from .resources import StudentResource, BusResource, BookingResource, BookingOTPResource


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


class StopInline(admin.TabularInline):
    model = Stop
    extra = 1
    fields = ('stop_name', 'location', 'is_pickup', 'is_dropoff', 'is_active')


# Users Group - Students
@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = StudentResource
    list_display = ('email', 'first_name', 'last_name', 'roll_no', 'dept', 'year', 'is_active', 'has_active_booking')
    list_filter = ('year', 'dept', 'gender', 'student_type', 'degree_type', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'roll_no')
    ordering = ('email',)
    filter_horizontal = ()
    readonly_fields = ('last_login', 'date_joined', 'has_active_booking')
    
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

    def has_active_booking(self, obj):
        return obj.has_active_booking()
    has_active_booking.boolean = True
    has_active_booking.short_description = 'Active Booking'


# Booking Group - Booking and BookingOTP
class BookingOTPInline(admin.TabularInline):
    model = BookingOTP
    extra = 0
    readonly_fields = ('otp_code', 'created_at', 'expires_at', 'verified')
    can_delete = False


@admin.register(Booking)
class BookingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = BookingResource
    list_display = ('student', 'bus', 'booking_date', 'trip_date', 'departure_time', 'from_location', 'to_location', 'selected_stop_display', 'status', 'otp_code')
    list_filter = ('bus__route_name', 'trip_date', 'departure_time', 'booking_date', 'status')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'bus__bus_no', 'from_location', 'to_location', 'selected_stop__stop_name', 'selected_stop__location')
    ordering = ('-booking_date',)
    readonly_fields = ('booking_date', 'otp_code')
    inlines = [BookingOTPInline]
    
    fieldsets = (
        ('Basic Info', {'fields': ('student', 'bus')}),
        ('Trip Details', {'fields': ('trip_date', 'departure_time', 'from_location', 'to_location', 'selected_stop')}),
        ('System Info', {'fields': ('booking_date', 'status')}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('booking_date',)
        return ()

    def selected_stop_display(self, obj):
        if obj.selected_stop:
            return f"{obj.selected_stop.stop_name} ({obj.selected_stop.location})"
        return '-'
    selected_stop_display.short_description = 'Selected Stop'

    def otp_code(self, obj):
        if hasattr(obj, 'otp') and obj.otp:
            return obj.otp.otp_code
        return '-'
    otp_code.short_description = 'OTP Code'


@admin.register(BookingOTP)
class BookingOTPAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = BookingOTPResource
    list_display = ('booking', 'otp_code', 'created_at', 'expires_at', 'verified', 'is_expired', 'time_remaining')
    list_filter = ('verified', 'created_at', 'expires_at')
    search_fields = ('booking__student__email', 'booking__student__first_name', 'otp_code')
    ordering = ('-created_at',)
    readonly_fields = ('otp_code', 'created_at', 'expires_at')
    actions = ['resend_expired_otps']
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('booking', 'otp_code', 'created_at', 'expires_at', 'verified')
        }),
        ('Actions', {
            'fields': (),
            'description': 'Use the "Resend OTP" action below for expired OTPs'
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def time_remaining(self, obj):
        if obj.is_expired():
            return "Expired"
        remaining = obj.expires_at - timezone.now()
        minutes = int(remaining.total_seconds() // 60)
        seconds = int(remaining.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    time_remaining.short_description = 'Time Remaining'
    
    def resend_expired_otps(self, request, queryset):
        """Admin action to resend OTPs for expired entries"""
        expired_otps = queryset.filter(expires_at__lt=timezone.now())
        count = 0
        
        for otp in expired_otps:
            try:
                otp.regenerate_otp()
                count += 1
            except Exception as e:
                self.message_user(request, f"Failed to resend OTP for booking {otp.booking.id}: {str(e)}", level='ERROR')
        
        if count > 0:
            self.message_user(request, f"Successfully resent {count} OTP(s)")
        else:
            self.message_user(request, "No expired OTPs found in the selection")
    
    resend_expired_otps.short_description = "Resend OTP for expired entries"
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        # Add a custom action for resending individual OTP
        actions['resend_single_otp'] = (self.resend_single_otp, 'resend_single_otp', "Resend OTP")
        return actions
    
    def resend_single_otp(self, modeladmin, request, queryset):
        """Resend OTP for a single booking"""
        if len(queryset) != 1:
            self.message_user(request, "Please select exactly one OTP to resend", level='ERROR')
            return
        
        otp = queryset.first()
        try:
            new_otp = otp.regenerate_otp()
            self.message_user(request, f"OTP resent successfully. New OTP: {new_otp}")
        except Exception as e:
            self.message_user(request, f"Failed to resend OTP: {str(e)}", level='ERROR')
    
    resend_single_otp.short_description = "Resend OTP"


# Bus Details Group - Buses and Stops
@admin.register(Bus)
class BusAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = BusResource
    form = BusAdminForm
    list_display = ('bus_no', 'route_name', 'from_location', 'to_location', 'departure_date', 'departure_time', 'capacity', 'available_seats', 'is_full')
    list_filter = (DepartureDateFilter, 'route_name', 'from_location', 'to_location')
    search_fields = ('bus_no', 'route_name', 'from_location', 'to_location')
    ordering = ('bus_no',)
    actions = ['set_today_departure', 'set_tomorrow_departure', 'set_next_week_departure']
    readonly_fields = ('available_seats', 'is_full')
    inlines = [StopInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('bus_no', 'route_name', 'from_location', 'to_location')
        }),
        ('Schedule', {
            'fields': ('departure_date', 'departure_time')
        }),
        ('Capacity', {
            'fields': ('capacity',)
        }),
    )
    
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


@admin.register(Stop)
class StopAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('bus', 'stop_name', 'location', 'is_pickup', 'is_dropoff', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_pickup', 'is_dropoff', 'bus__route_name', 'created_at')
    search_fields = ('bus__bus_no', 'stop_name', 'location')
    ordering = ('bus__bus_no', 'stop_name', 'location')
    list_editable = ('is_active', 'is_pickup', 'is_dropoff')
    
    fieldsets = (
        ('Stop Information', {
            'fields': ('bus', 'stop_name', 'location')
        }),
        ('Stop Type', {
            'fields': ('is_pickup', 'is_dropoff')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


# Customize admin site
admin.site.site_header = "Bus Booking System Administration"
admin.site.site_title = "Bus Booking Admin"
admin.site.index_title = "Welcome to Bus Booking System"

# Customize the admin app list to show the desired structure

# Customize the admin app list to show the desired structure
def get_app_list(request):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    app_dict = {}

    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label

        if app_label not in app_dict:
            app_dict[app_label] = {
                'name': app_label.title(),
                'app_label': app_label,
                'app_url': '/admin/%s/' % app_label,
                'has_module_perms': True,
                'models': [],
            }

        if model_admin.has_view_permission(request):
            model_dict = {
                'name': model._meta.verbose_name_plural,
                'object_name': model._meta.object_name,
                'perms': model_admin.get_model_perms(request),
                'admin_url': None,
                'add_url': None,
            }
            
            if model_admin.has_change_permission(request):
                model_dict['admin_url'] = '/admin/%s/%s/' % (app_label, model._meta.model_name)
            if model_admin.has_add_permission(request):
                model_dict['add_url'] = '/admin/%s/%s/add/' % (app_label, model._meta.model_name)
                
            app_dict[app_label]['models'].append(model_dict)

    # Custom grouping for the booking app
    if 'booking' in app_dict:
        booking_app = app_dict['booking']
        
        # Create custom structure
        custom_apps = []
        
        # Users group
        users_app = {
            'name': 'Users',
            'app_label': 'users',
            'app_url': '/admin/booking/student/',
            'has_module_perms': True,
            'models': [m for m in booking_app['models'] if m['object_name'] == 'Student']
        }
        custom_apps.append(users_app)
        
        # Booking group
        booking_group_app = {
            'name': 'Booking',
            'app_label': 'booking_group',
            'app_url': '/admin/booking/booking/',
            'has_module_perms': True,
            'models': [m for m in booking_app['models'] if m['object_name'] in ['Booking', 'BookingOTP']]
        }
        custom_apps.append(booking_group_app)
        
        # Bus Details group
        bus_details_app = {
            'name': 'Bus Details',
            'app_label': 'bus_details',
            'app_url': '/admin/booking/bus/',
            'has_module_perms': True,
            'models': [m for m in booking_app['models'] if m['object_name'] in ['Bus', 'Stop']]
        }
        custom_apps.append(bus_details_app)
        
        # Remove the original booking app and add our custom structure
        del app_dict['booking']
        for app in custom_apps:
            if app['models']:  # Only add apps that have models
                app_dict[app['app_label']] = app

    # Filter out auth groups and other unwanted apps
    filtered_apps = []
    for app in app_dict.values():
        # Skip auth groups and other unwanted apps
        if app['app_label'] not in ['auth', 'sessions', 'contenttypes']:
            filtered_apps.append(app)
    
    return sorted(filtered_apps, key=lambda x: x['name'].lower())

# Override the default get_app_list method
admin.site.get_app_list = get_app_list