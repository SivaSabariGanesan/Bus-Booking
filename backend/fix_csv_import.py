#!/usr/bin/env python
"""
Quick fix script for CSV import issues in the Bus Booking System.

This script provides alternative methods to import students when the Django admin
interface encounters file path or upload issues.

Usage:
    python fix_csv_import.py --help
    python fix_csv_import.py import test_students.csv
    python fix_csv_import.py import students.csv --update
    python fix_csv_import.py import students.csv --dry-run
"""

import os
import sys
import csv
import argparse
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_booking.settings')

import django
django.setup()

from booking.models import Student
from django.contrib.auth.hashers import make_password


def validate_csv_file(csv_file):
    """Validate CSV file format and content."""
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    
    if not csv_file.lower().endswith('.csv'):
        raise ValueError("File must be a CSV file")
    
    return True


def validate_row(row, row_num):
    """Validate a single row of data."""
    required_fields = ['first_name', 'last_name', 'email', 'roll_no', 'dept', 'year', 'gender']
    
    # Check for missing required fields
    missing_fields = [field for field in required_fields if not row.get(field, '').strip()]
    if missing_fields:
        raise ValueError(f"Row {row_num}: Missing required fields: {', '.join(missing_fields)}")
    
    # Validate email format
    email = row['email'].strip().lower()
    if '@' not in email:
        raise ValueError(f"Row {row_num}: Invalid email format: {email}")
    
    # Validate year
    year = row['year'].strip()
    if year not in ['1', '2', '3', '4']:
        raise ValueError(f"Row {row_num}: Invalid year: {year}. Must be 1, 2, 3, or 4")
    
    # Validate gender
    gender = row['gender'].strip().upper()
    if gender not in ['M', 'F', 'O']:
        raise ValueError(f"Row {row_num}: Invalid gender: {gender}. Must be M, F, or O")
    
    return True


def import_students(csv_file, update_existing=False, dry_run=False):
    """Import students from CSV file."""
    print(f"Starting import from: {csv_file}")
    print(f"Update existing: {update_existing}")
    print(f"Dry run: {dry_run}")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    update_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Validate required columns
            required_columns = ['first_name', 'last_name', 'email', 'roll_no', 'dept', 'year', 'gender']
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validate row data
                    validate_row(row, row_num)
                    
                    # Clean data
                    email = row['email'].strip().lower()
                    first_name = row['first_name'].strip()
                    last_name = row['last_name'].strip()
                    roll_no = row['roll_no'].strip()
                    dept = row['dept'].strip()
                    year = row['year'].strip()
                    gender = row['gender'].strip().upper()
                    phone_number = row.get('phone_number', '').strip()
                    
                    # Check if student already exists
                    existing_student = None
                    try:
                        existing_student = Student.objects.get(email=email)
                    except Student.DoesNotExist:
                        pass
                    
                    if existing_student:
                        if update_existing:
                            # Update existing student
                            if not dry_run:
                                existing_student.first_name = first_name
                                existing_student.last_name = last_name
                                existing_student.roll_no = roll_no
                                existing_student.dept = dept
                                existing_student.year = year
                                existing_student.gender = gender
                                if phone_number:
                                    existing_student.phone_number = phone_number
                                existing_student.save()
                            
                            print(f"✓ Row {row_num}: Updated student {email}")
                            update_count += 1
                        else:
                            print(f"⚠ Row {row_num}: Student {email} already exists (use --update to update)")
                            error_count += 1
                    else:
                        # Create new student
                        if not dry_run:
                            Student.objects.create(
                                email=email,
                                first_name=first_name,
                                last_name=last_name,
                                roll_no=roll_no,
                                dept=dept,
                                year=year,
                                gender=gender,
                                phone_number=phone_number,
                                password=make_password('Changeme@123')
                            )
                        
                        print(f"✓ Row {row_num}: Created student {email}")
                        success_count += 1
                
                except Exception as e:
                    print(f"✗ Row {row_num}: Error - {str(e)}")
                    error_count += 1
    
    except UnicodeDecodeError:
        print("✗ Error: File encoding issue. Please save the CSV file as UTF-8.")
        return
    except Exception as e:
        print(f"✗ Error reading CSV file: {str(e)}")
        return
    
    # Summary
    print("\n" + "="*50)
    print("IMPORT SUMMARY")
    print("="*50)
    
    if dry_run:
        print("DRY RUN - No changes made")
    
    print(f"Successfully processed: {success_count}")
    if update_existing:
        print(f"Updated existing students: {update_count}")
    print(f"Errors: {error_count}")
    print(f"Total rows processed: {success_count + update_count + error_count}")
    
    if error_count > 0:
        print("\n⚠ Some rows had errors. Check the output above for details.")
    
    if success_count > 0 and not dry_run:
        print(f"\n✅ Import completed! {success_count} students imported with default password 'Changeme@123'")


def create_template():
    """Create a sample CSV template."""
    template_file = "students_template.csv"
    
    with open(template_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['first_name', 'last_name', 'email', 'phone_number', 'year', 'roll_no', 'dept', 'gender'])
        writer.writerow(['John', 'Doe', 'john.doe@example.com', '1234567890', '1', '2023001', 'Computer Science', 'M'])
        writer.writerow(['Jane', 'Smith', 'jane.smith@example.com', '9876543210', '2', '2022001', 'Electrical Engineering', 'F'])
        writer.writerow(['Mike', 'Johnson', 'mike.johnson@example.com', '5551234567', '3', '2021001', 'Mechanical Engineering', 'M'])
    
    print(f"✅ Template created: {template_file}")
    print("You can now edit this file and use it for importing students.")


def main():
    parser = argparse.ArgumentParser(description='Fix CSV import issues for Bus Booking System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import students from CSV file')
    import_parser.add_argument('csv_file', help='Path to the CSV file')
    import_parser.add_argument('--update', action='store_true', help='Update existing students')
    import_parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without importing')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Create a sample CSV template')
    
    args = parser.parse_args()
    
    if args.command == 'import':
        try:
            validate_csv_file(args.csv_file)
            import_students(args.csv_file, args.update, args.dry_run)
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            sys.exit(1)
    
    elif args.command == 'template':
        create_template()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
