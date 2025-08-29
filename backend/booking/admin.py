from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from datetime import timedelta
from import_export.admin import ImportExportModelAdmin
from .models import Student, Bus, Booking, BookingOTP, Stop, SiteConfiguration
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
    list_filter = ('year', 'dept', 'gender', 'is_active')
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
            'fields': ('roll_no', 'dept', 'year')
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
                      'phone_number', 'roll_no', 'dept', 'year', 'gender'),
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
    # Django admin list_filter does not support traversing to a specific field on a related
    # model using double-underscore syntax. Using 'bus__route_name' raises a FieldError in
    # production (500 on the changelist). Filter by the related object instead.
    list_filter = ('bus', 'trip_date', 'departure_time', 'booking_date', 'status')
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


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        # Rename in sidebar
        perms['change'] = True
        return perms
    def get_queryset(self, request):
        return super().get_queryset(request)
    def get_admin_name(self):
        return 'Configuration'
    get_admin_name.short_description = 'Configuration'
    get_admin_name.admin_order_field = 'Configuration'


# Customize admin site
admin.site.site_header = "Bus Booking System Administration"
admin.site.site_title = "Bus Booking Admin"
admin.site.index_title = "Welcome to Bus Booking System"

# Custom admin grouping for sidebar/app list while preserving functionality
_original_get_app_list = admin.site.get_app_list

def _group_booking_app_list(request):
    """Return a custom grouped app list for the `booking` app only.

    Groups:
    - Bookings: Booking otp, Bookings
    - Bus Details: Buses, Stops
    - Users and groups: Students
    Any other apps remain as-is below these groups.
    """
    try:
        app_dict = admin.site._build_app_dict(request)
    except Exception:
        return _original_get_app_list(request)

    booking_app = app_dict.get('booking')
    if not booking_app:
        return _original_get_app_list(request)

    model_by_object_name = {m['object_name']: m for m in booking_app['models']}

    def pick(object_names):
        items = []
        for name in object_names:
            model_info = model_by_object_name.get(name)
            if model_info:
                items.append(model_info)
        return items

    grouped = [
        {
            'name': 'Bookings',
            'app_label': 'bookings',
            'app_url': '',
            'has_module_perms': True,
            'models': pick(['BookingOTP', 'Booking']),
        },
        {
            'name': 'Bus Details',
            'app_label': 'bus_details',
            'app_url': '',
            'has_module_perms': True,
            'models': pick(['Bus', 'Stop']),
        },
        {
            'name': 'Users and groups',
            'app_label': 'users_and_groups',
            'app_url': '',
            'has_module_perms': True,
            'models': pick(['Student', 'SiteConfiguration']),
        },
    ]

    others = [app for app in _original_get_app_list(request) if app.get('app_label') != 'booking']
    return grouped + others


def custom_get_app_list(request):
    try:
        return _group_booking_app_list(request)
    except Exception:
        return _original_get_app_list(request)


admin.site.get_app_list = custom_get_app_list