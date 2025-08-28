# CSV Import Guide for Bus Booking System

This guide explains how to use the CSV import functionality in the Django admin panel for the Bus Booking System.

## Overview

The system now supports importing data from CSV files for all major models:
- Students
- Buses
- Bookings
- Booking OTPs

## How to Import CSV Data

### 1. Access the Admin Panel
- Go to `/admin/` in your browser
- Log in with your superuser credentials

### 2. Navigate to the Model
- Click on the model you want to import data for (e.g., "Students", "Buses", etc.)
- You'll see an "IMPORT" button at the top of the list view

### 3. Import Process
- Click the "IMPORT" button
- Choose your CSV file
- Review the import preview
- Click "Confirm import" to proceed

## CSV File Format Requirements

### Students Template
```csv
email,first_name,last_name,phone_number,year,roll_no,dept,gender,student_type,degree_type,is_active,is_staff,is_superuser
student@example.com,John,Doe,1234567890,1,2023001,Computer Science,M,REGULAR,BTECH,True,False,False
```

**Required Fields:**
- `email`: Unique email address
- `first_name`: Student's first name
- `last_name`: Student's last name
- `roll_no`: Unique roll number
- `dept`: Department name
- `year`: Year of study (1, 2, 3, or 4)
- `gender`: M, F, or O
- `student_type`: REGULAR or LATERAL
- `degree_type`: BTECH, MTECH, MBA, BBA, BCA, or MCA

**Optional Fields:**
- `phone_number`: Phone number
- `is_active`: True/False (default: True)
- `is_staff`: True/False (default: False)
- `is_superuser`: True/False (default: False)

### Buses Template
```csv
bus_no,route_name,from_location,to_location,departure_date,departure_time,capacity
BUS001,Campus to City Center,Campus,City Center,2024-01-15,08:00,50
```

**Required Fields:**
- `bus_no`: Unique bus number
- `route_name`: Name of the route
- `from_location`: Starting location
- `to_location`: Destination
- `departure_date`: Date in YYYY-MM-DD format
- `departure_time`: Time in HH:MM format (24-hour)
- `capacity`: Number of seats

### Bookings Template
```csv
id,student_email,bus_no,trip_date,departure_time,from_location,to_location,status
1,student@example.com,BUS001,2024-01-15,08:00,Campus,City Center,CONFIRMED
```

**Required Fields:**
- `student_email`: Must match an existing student's email
- `bus_no`: Must match an existing bus number
- `trip_date`: Date in YYYY-MM-DD format
- `departure_time`: Time in HH:MM format (24-hour)
- `from_location`: Starting location
- `to_location`: Destination
- `status`: Booking status

**Optional Fields:**
- `id`: Leave empty for new bookings

## Important Notes

### Data Validation
- The system validates all imported data
- Foreign key relationships must exist (e.g., student_email must match an existing student)
- Date and time formats must be exact
- Required fields cannot be empty

### Password Handling
- For students, if you include a password field, it will be automatically hashed
- If no password is provided, the student won't be able to log in until reset

### Duplicate Handling
- Students: Uses email as the unique identifier
- Buses: Uses bus_no as the unique identifier
- Bookings: Uses ID as the unique identifier

### Error Handling
- Import errors are displayed in the admin interface
- Failed rows are clearly marked
- You can review and fix errors before confirming the import

## Download Templates

Sample CSV templates are available in the `static/csv_templates/` directory:
- `students_template.csv`
- `buses_template.csv`
- `bookings_template.csv`

## Export Functionality

You can also export existing data to CSV:
- Click the "EXPORT" button in any model's admin view
- Choose the format (CSV, JSON, XLS, etc.)
- Download the file

## Troubleshooting

### Common Issues
1. **Date Format Errors**: Ensure dates are in YYYY-MM-DD format
2. **Time Format Errors**: Ensure times are in HH:MM format (24-hour)
3. **Foreign Key Errors**: Ensure referenced records exist
4. **Required Field Missing**: Check that all required fields are populated

### Getting Help
- Check the Django admin error messages
- Verify your CSV format matches the templates
- Ensure all referenced data exists in the system

## Security Considerations

- Only superusers can access the import functionality
- All imported data is validated and sanitized
- Passwords are automatically hashed
- The system prevents SQL injection and other attacks
