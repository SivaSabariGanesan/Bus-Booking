from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student, Bus, Booking


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


class BusAdminForm(forms.ModelForm):
    weekend_dates_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter dates separated by commas (e.g., 2024-01-06, 2024-01-13, 2024-01-20)'}),
        required=False,
        help_text="Enter weekend dates separated by commas (YYYY-MM-DD format)"
    )
    return_dates_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter dates separated by commas (e.g., 2024-01-08, 2024-01-15, 2024-01-22)'}),
        required=False,
        help_text="Enter return trip dates separated by commas (YYYY-MM-DD format)"
    )

    class Meta:
        model = Bus
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Convert JSON lists to comma-separated strings for display
            self.fields['weekend_dates_input'].initial = ', '.join(self.instance.weekend_dates) if self.instance.weekend_dates else ''
            self.fields['return_dates_input'].initial = ', '.join(self.instance.return_dates) if self.instance.return_dates else ''

    def clean_weekend_dates_input(self):
        data = self.cleaned_data['weekend_dates_input']
        if data:
            dates = [date.strip() for date in data.split(',') if date.strip()]
            # Validate date format
            from datetime import datetime
            valid_dates = []
            for date_str in dates:
                try:
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    # Check if it's actually a weekend
                    if parsed_date.weekday() in [5, 6]:  # Saturday or Sunday
                        valid_dates.append(date_str)
                    else:
                        self.add_error('weekend_dates_input', f'{date_str} is not a weekend date')
                except ValueError:
                    self.add_error('weekend_dates_input', f'{date_str} is not a valid date (use YYYY-MM-DD format)')
            return valid_dates
        return []

    def clean_return_dates_input(self):
        data = self.cleaned_data['return_dates_input']
        if data:
            dates = [date.strip() for date in data.split(',') if date.strip()]
            # Validate date format
            from datetime import datetime
            valid_dates = []
            for date_str in dates:
                try:
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    # Check if it's a weekday
                    if parsed_date.weekday() not in [5, 6]:  # Not Saturday or Sunday
                        valid_dates.append(date_str)
                    else:
                        self.add_error('return_dates_input', f'{date_str} is a weekend date, not suitable for return trips')
                except ValueError:
                    self.add_error('return_dates_input', f'{date_str} is not a valid date (use YYYY-MM-DD format)')
            return valid_dates
        return []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.weekend_dates = self.cleaned_data['weekend_dates_input']
        instance.return_dates = self.cleaned_data['return_dates_input']
        if commit:
            instance.save()
        return instance

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    form = BusAdminForm
    list_display = ('bus_no', 'route_name', 'from_location', 'to_location', 'trip_types', 'departure_time', 'return_time', 'capacity', 'available_seats')
    list_filter = ('route_name', 'from_location', 'to_location', 'trip_types')
    search_fields = ('bus_no', 'route_name', 'from_location', 'to_location')
    ordering = ('bus_no',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('bus_no', 'route_name', 'from_location', 'to_location')
        }),
        ('Trip Configuration', {
            'fields': ('trip_types', 'weekend_dates_input', 'return_dates_input'),
            'description': 'Select trip types and specify available dates for each type'
        }),
        ('Schedule', {
            'fields': ('departure_time', 'return_time')
        }),
        ('Capacity', {
            'fields': ('capacity',)
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'bus', 'booking_date', 'trip_date', 'departure_time', 'return_time', 'is_return_trip', 'trip_type', 'from_location', 'to_location')
    list_filter = ('bus__route_name', 'is_return_trip', 'trip_type', 'trip_date', 'departure_time', 'booking_date')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'bus__bus_no', 'from_location', 'to_location')
    ordering = ('-booking_date',)
    
    fieldsets = (
        ('Basic Info', {'fields': ('student', 'bus', 'trip_type')}),
        ('Trip Details', {'fields': ('trip_date', 'departure_time', 'return_time', 'from_location', 'to_location')}),
        ('System Info', {'fields': ('booking_date', 'is_return_trip')}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('booking_date',)
        return ()