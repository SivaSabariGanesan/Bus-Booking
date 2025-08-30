# CSV Import Troubleshooting Guide

## Common Issues and Solutions

### 1. FileNotFoundError: The system cannot find the file specified

**Problem**: This error occurs when Django can't locate the CSV file during import.

**Causes**:
- File path issues on Windows
- File permissions
- File not properly uploaded
- Temporary file cleanup issues

**Solutions**:

#### A. Check File Upload
1. **Verify File Selection**: Make sure you've selected a valid CSV file
2. **File Format**: Ensure the file is actually a CSV file (not Excel or other format)
3. **File Size**: Check if the file is too large (should be under 10MB for web uploads)

#### B. Use the Template Download Feature
1. Go to the Students admin page
2. Look for a "Download Template" link (if available)
3. Download the template and use it as a base for your data

#### C. Manual File Preparation
Create your CSV file manually with this exact format:

```csv
first_name,last_name,email,phone_number,year,roll_no,dept,gender
John,Doe,john.doe@example.com,1234567890,1,2023001,Computer Science,M
Jane,Smith,jane.smith@example.com,9876543210,2,2022001,Electrical Engineering,F
```

#### D. Alternative Import Methods

**Method 1: Direct Database Import**
```bash
# If you have access to the server, you can use Django shell
python manage.py shell

# In the shell:
from booking.models import Student
from django.contrib.auth.hashers import make_password
import csv

with open('students.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        Student.objects.create(
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            phone_number=row['phone_number'],
            year=row['year'],
            roll_no=row['roll_no'],
            dept=row['dept'],
            gender=row['gender'],
            password=make_password('Changeme@123')
        )
```

**Method 2: Use Django Management Command**
Create a custom management command for bulk imports.

### 2. Import Validation Errors

**Common Validation Issues**:

#### A. Email Already Exists
- **Error**: "Student with this Email already exists"
- **Solution**: Use the `import_id_fields = ('email',)` setting to update existing records

#### B. Invalid Date/Time Format
- **Error**: "Invalid date format"
- **Solution**: Use YYYY-MM-DD format for dates, HH:MM for times

#### C. Missing Required Fields
- **Error**: "This field is required"
- **Solution**: Ensure all required fields are populated

### 3. Windows-Specific Issues

#### A. File Path Problems
Windows uses backslashes in file paths, which can cause issues.

**Solution**: Use forward slashes or raw strings:
```python
# Good
template_path = os.path.join(settings.BASE_DIR, 'static', 'csv_templates', 'students_template.csv')

# Or use raw string
template_path = r'C:\path\to\your\file.csv'
```

#### B. File Encoding Issues
**Problem**: Special characters not displaying correctly

**Solution**: 
1. Save your CSV file as UTF-8
2. Use this format when opening files:
```python
with open('file.csv', 'r', encoding='utf-8') as f:
    # process file
```

### 4. Browser-Specific Issues

#### A. File Upload Size Limits
**Problem**: Large files fail to upload

**Solution**:
1. Check your web server's upload limit (nginx, Apache)
2. Split large files into smaller chunks
3. Use direct database import for large datasets

#### B. Browser Cache Issues
**Problem**: Old file data persists

**Solution**:
1. Clear browser cache
2. Use incognito/private browsing mode
3. Try a different browser

### 5. Server Configuration Issues

#### A. Temporary File Directory
**Problem**: Server can't write to temp directory

**Solution**: Check Django's `FILE_UPLOAD_TEMP_DIR` setting:
```python
# In settings.py
FILE_UPLOAD_TEMP_DIR = '/tmp'  # or appropriate directory
```

#### B. File Permissions
**Problem**: Permission denied errors

**Solution**: Ensure the web server has write permissions to the upload directory.

### 6. Step-by-Step Import Process

#### Step 1: Prepare Your Data
1. Download the template: `/admin/booking/student/download-template/`
2. Fill in your data following the template format
3. Save as UTF-8 CSV

#### Step 2: Validate Your Data
1. Check for required fields
2. Verify email formats
3. Ensure unique roll numbers
4. Validate date/time formats

#### Step 3: Import Process
1. Go to `/admin/booking/student/`
2. Click "IMPORT" button
3. Select your CSV file
4. Review the preview
5. Click "Confirm import"

#### Step 4: Post-Import Verification
1. Check the password status column
2. Verify all students were imported
3. Test login with default password

### 7. Emergency Import Methods

#### A. Django Admin Manual Entry
For small datasets, manually enter students through the admin interface.

#### B. Django Shell Import
```python
python manage.py shell

from booking.models import Student
from django.contrib.auth.hashers import make_password

# Create a single student
student = Student.objects.create(
    email='test@example.com',
    first_name='Test',
    last_name='User',
    phone_number='1234567890',
    year='1',
    roll_no='2023001',
    dept='Computer Science',
    gender='M',
    password=make_password('Changeme@123')
)
```

#### C. SQL Direct Import (Advanced)
For very large datasets, consider direct SQL import (use with caution).

### 8. Debugging Tips

#### A. Enable Debug Mode
Set `DEBUG = True` in settings to see detailed error messages.

#### B. Check Logs
Look at Django logs for detailed error information:
```bash
python manage.py runserver --verbosity=2
```

#### C. Test with Small File
Start with a single row to test the import process.

### 9. Prevention Tips

1. **Always backup your database** before bulk imports
2. **Test imports** with a small subset first
3. **Validate data** before importing
4. **Use templates** to ensure correct format
5. **Monitor import results** carefully

### 10. Getting Help

If you continue to have issues:

1. Check the Django admin error messages
2. Look at the browser's developer console
3. Check the server logs
4. Try the alternative import methods above
5. Contact system administrator with specific error details

## Quick Fix Checklist

- [ ] File is valid CSV format
- [ ] File is saved as UTF-8
- [ ] All required fields are present
- [ ] Email addresses are unique
- [ ] Date/time formats are correct
- [ ] File size is reasonable (< 10MB)
- [ ] Browser cache is cleared
- [ ] Server has proper permissions
- [ ] Database is backed up
