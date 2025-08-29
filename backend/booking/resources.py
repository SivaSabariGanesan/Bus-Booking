from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateWidget, TimeWidget
from .models import Student, Bus, Booking, BookingOTP


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('email',)
        fields = (
            'first_name', 'last_name', 'email', 'phone_number', 
            'year', 'roll_no', 'dept', 'gender'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True
        
    def before_import_row(self, row, **kwargs):
        """Set default password for all imported students"""
        from django.contrib.auth.hashers import make_password
        # Set default password for all imported students
        row['password'] = make_password('Changeme@123')
        return row


class BusResource(resources.ModelResource):
    departure_date = fields.Field(
        column_name='departure_date',
        attribute='departure_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    departure_time = fields.Field(
        column_name='departure_time',
        attribute='departure_time',
        widget=TimeWidget(format='%H:%M')
    )
    
    class Meta:
        model = Bus
        import_id_fields = ('bus_no',)
        fields = (
            'id', 'bus_no', 'route_name', 'from_location', 'to_location',
            'departure_date', 'departure_time', 'capacity', 'is_booking_open'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True


class BookingResource(resources.ModelResource):
    student = fields.Field(
        column_name='student_email',
        attribute='student',
        widget=ForeignKeyWidget(Student, 'email')
    )
    bus = fields.Field(
        column_name='bus_no',
        attribute='bus',
        widget=ForeignKeyWidget(Bus, 'bus_no')
    )
    selected_stop = fields.Field(
        column_name='selected_stop',
        attribute='selected_stop',
        widget=ForeignKeyWidget('booking.Stop', 'stop_name')
    )
    selected_stop_location = fields.Field(
        column_name='selected_stop_location',
        attribute='selected_stop__location'
    )
    trip_date = fields.Field(
        column_name='trip_date',
        attribute='trip_date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    departure_time = fields.Field(
        column_name='departure_time',
        attribute='departure_time',
        widget=TimeWidget(format='%H:%M')
    )
    
    class Meta:
        model = Booking
        import_id_fields = ('id',)
        fields = (
            'id', 'student', 'bus', 'trip_date', 'departure_time',
            'from_location', 'to_location', 'selected_stop', 'selected_stop_location', 'status'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True


class BookingOTPResource(resources.ModelResource):
    booking = fields.Field(
        column_name='booking_id',
        attribute='booking',
        widget=ForeignKeyWidget(Booking, 'id')
    )
    
    class Meta:
        model = BookingOTP
        import_id_fields = ('id',)
        fields = (
            'id', 'booking', 'otp_code', 'created_at', 'expires_at', 'verified'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True
