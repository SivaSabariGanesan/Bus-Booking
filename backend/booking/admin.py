from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime
from import_export.admin import ImportExportModelAdmin

from django.http import HttpResponse
from django.urls import path
from django.shortcuts import render
from django.contrib.admin import SimpleListFilter
import csv
from .models import Student, Bus, Booking, BookingOTP, Stop, SiteConfiguration
from .resources import StudentResource, BusResource, BookingResource, BookingOTPResource


def go_action(modeladmin, request, queryset):
    """Custom 'Go' action that can be used for any model"""
    from django.contrib import messages
    selected_count = queryset.count()
    model_name = modeladmin.model._meta.verbose_name_plural
    
    if selected_count == 0:
        messages.warning(request, f"No {model_name} selected.")
        return
    
    # Customize action based on the model
    if modeladmin.model == Student:
        # For students, you could activate/deactivate them, send emails, etc.
        active_count = queryset.filter(is_active=True).count()
        inactive_count = queryset.filter(is_active=False).count()
        messages.success(request, f"Selected {selected_count} students ({active_count} active, {inactive_count} inactive)")
        
    elif modeladmin.model == Bus:
        # For buses, you could open/close booking, update schedules, etc.
        open_count = queryset.filter(is_booking_open=True).count()
        closed_count = queryset.filter(is_booking_open=False).count()
        messages.success(request, f"Selected {selected_count} buses ({open_count} booking open, {closed_count} booking closed)")
        
    elif modeladmin.model == Booking:
        # For bookings, you could confirm/cancel them, etc.
        confirmed_count = queryset.filter(status='confirmed').count()
        pending_count = queryset.filter(status='pending').count()
        cancelled_count = queryset.filter(status='cancelled').count()
        messages.success(request, f"Selected {selected_count} bookings ({confirmed_count} confirmed, {pending_count} pending, {cancelled_count} cancelled)")
        
    elif modeladmin.model == BookingOTP:
        # For OTPs, you could resend them, etc.
        verified_count = queryset.filter(verified=True).count()
        unverified_count = queryset.filter(verified=False).count()
        expired_count = queryset.filter(expires_at__lt=timezone.now()).count()
        messages.success(request, f"Selected {selected_count} OTPs ({verified_count} verified, {unverified_count} unverified, {expired_count} expired)")
        
    elif modeladmin.model == Stop:
        # For stops, you could activate/deactivate them, etc.
        active_count = queryset.filter(is_active=True).count()
        inactive_count = queryset.filter(is_active=False).count()
        messages.success(request, f"Selected {selected_count} stops ({active_count} active, {inactive_count} inactive)")
        
    elif modeladmin.model == SiteConfiguration:
        # For site configuration, you could reload settings, etc.
        messages.success(request, f"Site configuration selected. Current allowed years: {queryset.first().allowed_years if queryset.exists() else 'Not set'}")
        
    else:
        messages.success(request, f"Processing {selected_count} selected {model_name}...")
    
    # You can add actual processing logic here based on your requirements
    # For example, you could redirect to a custom view or perform bulk operations

go_action.short_description = "Go - Process selected items"


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


class TripTypeFilter(SimpleListFilter):
    title = 'Trip Type'
    parameter_name = 'trip_type'

    def lookups(self, request, model_admin):
        return (
            ('outbound', 'Outbound (FROM REC)'),
            ('return', 'Return (TO REC)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'outbound':
            return queryset.filter(is_outbound_trip=True)
        if self.value() == 'return':
            return queryset.filter(is_outbound_trip=False)
        return queryset


class DateFilter(SimpleListFilter):
    title = 'Trip Date'
    parameter_name = 'trip_date'

    def lookups(self, request, model_admin):
        # Get unique trip dates from bookings
        dates = Booking.objects.dates('trip_date', 'day')
        return [(date.strftime('%Y-%m-%d'), date.strftime('%B %d, %Y')) for date in dates]

    def queryset(self, request, queryset):
        if self.value():
            try:
                date = datetime.strptime(self.value(), '%Y-%m-%d').date()
                return queryset.filter(trip_date=date)
            except ValueError:
                pass
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
    actions = [go_action]
    
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
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'student_name', 'bus_info', 'trip_type', 'trip_date', 
        'departure_time', 'from_location', 'to_location', 
        'status', 'booking_date', 'return_trip_available', 'swift_button'
    ]
    list_filter = [
        TripTypeFilter, DateFilter, 'status', 'trip_date', 
        'is_outbound_trip', 'booking_date'
    ]
    actions = ['auto_cancel_completed_outbound', go_action]
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_no', 'bus__bus_no']
    readonly_fields = ['return_trip_available']
    date_hierarchy = 'trip_date'
    
    def student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    student_name.short_description = 'Student Name'
    
    def bus_info(self, obj):
        return f"{obj.bus.bus_no} - {obj.bus.route_name}"
    bus_info.short_description = 'Bus Info'
    
    def trip_type(self, obj):
        return "Outbound (FROM REC)" if obj.is_outbound_trip else "Return (TO REC)"
    trip_type.short_description = 'Trip Type'
    
    def return_trip_available(self, obj):
        if obj.is_outbound_trip and obj.return_trip_available_after:
            if timezone.now() >= obj.return_trip_available_after:
                if obj.status == 'cancelled':
                    return "✅ Available (Outbound Cancelled)"
                else:
                    return "✅ Available"
            else:
                time_remaining = obj.return_trip_available_after - timezone.now()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                return f"⏳ {hours}h {minutes}m remaining"
        return "N/A"
    return_trip_available.short_description = 'Return Trip Status'
    
    def swift_button(self, obj):
        """Swift button to override 24-hour constraint immediately"""
        if not obj.is_outbound_trip:
            return "N/A (Return trip)"
        
        if not obj.return_trip_available_after:
            return "No restriction"
        
        now = timezone.now()
        if now >= obj.return_trip_available_after:
            # Auto-cancel outbound booking when 24 hours complete
            if obj.status != 'cancelled':
                obj.status = 'cancelled'
                obj.save()
            return "✅ Available (Outbound Cancelled)"
        else:
            html = f"""
            <a href="/admin/booking/booking/{obj.id}/swift-override/" 
               style="background: #28a745; color: white; padding: 6px 12px; 
                      text-decoration: none; border-radius: 4px; font-size: 12px; 
                      font-weight: bold; display: inline-block;">
               🚀 Swift
            </a>
            """
            return mark_safe(html)
    
    swift_button.short_description = 'Swift Override'
    
    def auto_cancel_completed_outbound(self, request, queryset):
        """Admin action to auto-cancel outbound bookings where 24-hour period is complete"""
        count = 0
        now = timezone.now()
        
        for booking in queryset:
            if (booking.is_outbound_trip and 
                booking.status in ['pending', 'confirmed'] and
                booking.return_trip_available_after and
                now >= booking.return_trip_available_after):
                
                # Cancel the outbound booking
                booking.status = 'cancelled'
                booking.save()
                count += 1
        
        if count > 0:
            self.message_user(
                request, 
                f"✅ {count} outbound booking(s) automatically cancelled (24-hour period completed)",
                level='SUCCESS'
            )
        else:
            self.message_user(
                request, 
                "ℹ️ No outbound bookings found that have completed their 24-hour period",
                level='INFO'
            )
    
    auto_cancel_completed_outbound.short_description = "🔄 Auto-cancel completed outbound bookings"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pickup-list/', self.admin_site.admin_view(self.pickup_list_view), name='booking_pickup_list'),
            path('dropoff-list/', self.admin_site.admin_view(self.dropoff_list_view), name='booking_dropoff_list'),
            path('export-pickup/', self.admin_site.admin_view(self.export_pickup_view), name='booking_export_pickup'),
            path('export-dropoff/', self.admin_site.admin_view(self.export_dropoff_view), name='booking_export_dropoff'),
            path('<int:booking_id>/swift-override/', self.admin_site.admin_view(self.swift_override_view), name='booking_swift_override'),
        ]
        return custom_urls + urls

    def pickup_list_view(self, request):
        """Admin view for pickup list with date filtering"""
        selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        
        try:
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
        
        # Get all outbound bookings (FROM REC) for the selected date
        pickups = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=True,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        context = {
            'title': f'Pickup List for {target_date.strftime("%B %d, %Y")}',
            'pickups': pickups,
            'selected_date': selected_date,
            'pickup_count': pickups.count(),
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/booking/pickup_list.html', context)

    def dropoff_list_view(self, request):
        """Admin view for drop-off list with date filtering"""
        selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        
        try:
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
        
        # Get all return bookings (TO REC) for the selected date
        dropoffs = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=False,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        context = {
            'title': f'Drop-off List for {target_date.strftime("%B %d, %Y")}',
            'dropoffs': dropoffs,
            'selected_date': selected_date,
            'dropoff_count': dropoffs.count(),
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/booking/dropoff_list.html', context)

    def export_pickup_view(self, request):
        """Export pickup list to CSV"""
        selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        
        try:
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
        
        # Get all outbound bookings (FROM REC) for the selected date
        pickups = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=True,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="pickup_list_{target_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Student Name', 'Roll No', 'Department', 'Phone', 
            'Pickup Location', 'Destination', 'Departure Time', 
            'Bus Number', 'Route Name', 'Status', 'Booking Date'
        ])
        
        for pickup in pickups:
            writer.writerow([
                f"{pickup.student.first_name} {pickup.student.last_name}",
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

    def export_dropoff_view(self, request):
        """Export drop-off list to CSV"""
        selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        
        try:
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
        
        # Get all return bookings (TO REC) for the selected date
        dropoffs = Booking.objects.filter(
            trip_date=target_date,
            is_outbound_trip=False,
            status__in=['pending', 'confirmed']
        ).select_related('student', 'bus').order_by('departure_time')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="dropoff_list_{target_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Student Name', 'Roll No', 'Department', 'Phone', 
            'Pickup Location', 'Drop-off Location', 'Departure Time', 
            'Bus Number', 'Route Name', 'Status', 'Booking Date'
        ])
        
        for dropoff in dropoffs:
            writer.writerow([
                f"{dropoff.student.first_name} {dropoff.student.last_name}",
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

    def swift_override_view(self, request, booking_id):
        """Swift override view to immediately remove 24-hour constraint"""
        try:
            booking = Booking.objects.get(id=booking_id)
            
            if not booking.is_outbound_trip:
                return HttpResponse(
                    "❌ This is not an outbound trip. Only outbound trips can use Swift override.",
                    content_type="text/html; charset=utf-8"
                )
            
            if not booking.return_trip_available_after:
                return HttpResponse(
                    "❌ No 24-hour constraint found for this booking.",
                    content_type="text/html; charset=utf-8"
                )
            
            # Swift override - remove 24-hour constraint immediately
            booking.return_trip_available_after = timezone.now()
            booking.save()
            
            # Auto-cancel the outbound booking so student can book return trip
            booking.status = 'cancelled'
            booking.save()
            
            # Redirect back to admin with success message
            from django.contrib import messages
            messages.success(request, f"🚀 Swift override applied! {booking.student.first_name} {booking.student.last_name}'s outbound booking cancelled. Student can now book return trip immediately!")
            
            from django.shortcuts import redirect
            return redirect('admin:booking_booking_changelist')
            
        except Booking.DoesNotExist:
            return HttpResponse(
                "❌ Booking not found.",
                content_type="text/html; charset=utf-8"
            )
        except Exception as e:
            return HttpResponse(
                f"❌ Error: {str(e)}",
                content_type="text/html; charset=utf-8"
            )


@admin.register(BookingOTP)
class BookingOTPAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = BookingOTPResource
    list_display = ('booking', 'otp_code', 'created_at', 'expires_at', 'verified', 'is_expired', 'time_remaining')
    list_filter = ('verified', 'created_at', 'expires_at')
    search_fields = ('booking__student__email', 'booking__student__first_name', 'otp_code')
    ordering = ('-created_at',)
    readonly_fields = ('otp_code', 'created_at', 'expires_at')
    actions = ['resend_expired_otps', go_action]
    
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
    list_display = ('bus_no', 'route_name', 'from_location', 'to_location', 'departure_date', 'departure_time', 'capacity', 'available_seats', 'is_full', 'is_booking_open', 'route_confirmed_today', 'required_buses_today')
    list_filter = (DepartureDateFilter, 'route_name', 'from_location', 'to_location', 'is_booking_open')
    search_fields = ('bus_no', 'route_name', 'from_location', 'to_location')
    ordering = ('bus_no',)
    actions = ['set_today_departure', 'set_tomorrow_departure', 'set_next_week_departure', go_action]
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
        ('Booking Controls', {
            'fields': ('is_booking_open',)
        }),
    )
    
    def route_confirmed_today(self, obj):
        try:
            return obj.confirmed_bookings_for_route_on_date()
        except Exception:
            return '-'
    route_confirmed_today.short_description = 'Route confirmed (today)'

    def required_buses_today(self, obj):
        try:
            return obj.required_buses_for_route_on_date()
        except Exception:
            return '-'
    required_buses_today.short_description = 'Required buses (today)'
    
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
    actions = [go_action]
    
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
    actions = [go_action]
    
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

    Groups in order:
    1. Authentication and Authorization
    2. Users and groups: Students, SiteConfiguration
    3. Bookings: BookingOTP, Booking
    4. Bus Details: Buses, Stops
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

    # Get Django's built-in auth models
    auth_app = app_dict.get('auth')
    auth_models = auth_app['models'] if auth_app else []

    grouped = [
        {
            'name': 'Authentication and Authorization',
            'app_label': 'auth',
            'app_url': '',
            'has_module_perms': True,
            'models': auth_models,  # Include Django's built-in auth models
        },
        {
            'name': 'Users and groups',
            'app_label': 'users_and_groups',
            'app_url': '',
            'has_module_perms': True,
            'models': pick(['Student', 'SiteConfiguration']),
        },
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
    ]

    # Filter out auth and booking apps from others since we're handling them separately
    others = [app for app in _original_get_app_list(request) 
              if app.get('app_label') not in ['booking', 'auth']]
    return grouped + others


def custom_get_app_list(request):
    try:
        return _group_booking_app_list(request)
    except Exception:
        return _original_get_app_list(request)


admin.site.get_app_list = custom_get_app_list