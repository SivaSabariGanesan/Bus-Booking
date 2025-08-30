from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from booking.models import Student
import csv
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Import students from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing students instead of creating new ones',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        update_existing = options['update']
        dry_run = options['dry_run']

        # Check if file exists
        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file not found: {csv_file}')

        # Validate file extension
        if not csv_file.lower().endswith('.csv'):
            raise CommandError('File must be a CSV file')

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Validate required columns
                required_columns = ['first_name', 'last_name', 'email', 'roll_no', 'dept', 'year', 'gender']
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                
                if missing_columns:
                    raise CommandError(f'Missing required columns: {", ".join(missing_columns)}')

                success_count = 0
                error_count = 0
                update_count = 0

                for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                    try:
                        # Clean and validate data
                        email = row['email'].strip().lower()
                        first_name = row['first_name'].strip()
                        last_name = row['last_name'].strip()
                        roll_no = row['roll_no'].strip()
                        dept = row['dept'].strip()
                        year = row['year'].strip()
                        gender = row['gender'].strip().upper()
                        phone_number = row.get('phone_number', '').strip()

                        # Validate required fields
                        if not all([email, first_name, last_name, roll_no, dept, year, gender]):
                            self.stdout.write(
                                self.style.ERROR(f'Row {row_num}: Missing required fields')
                            )
                            error_count += 1
                            continue

                        # Validate email format
                        if '@' not in email:
                            self.stdout.write(
                                self.style.ERROR(f'Row {row_num}: Invalid email format: {email}')
                            )
                            error_count += 1
                            continue

                        # Validate year
                        if year not in ['1', '2', '3', '4']:
                            self.stdout.write(
                                self.style.ERROR(f'Row {row_num}: Invalid year: {year}. Must be 1, 2, 3, or 4')
                            )
                            error_count += 1
                            continue

                        # Validate gender
                        if gender not in ['M', 'F', 'O']:
                            self.stdout.write(
                                self.style.ERROR(f'Row {row_num}: Invalid gender: {gender}. Must be M, F, or O')
                            )
                            error_count += 1
                            continue

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
                                
                                self.stdout.write(
                                    self.style.SUCCESS(f'Row {row_num}: Updated student {email}')
                                )
                                update_count += 1
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f'Row {row_num}: Student {email} already exists (use --update to update)')
                                )
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
                            
                            self.stdout.write(
                                self.style.SUCCESS(f'Row {row_num}: Created student {email}')
                            )
                            success_count += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Row {row_num}: Error processing row: {str(e)}')
                        )
                        error_count += 1

                # Summary
                self.stdout.write('\n' + '='*50)
                self.stdout.write('IMPORT SUMMARY')
                self.stdout.write('='*50)
                
                if dry_run:
                    self.stdout.write(f'DRY RUN - No changes made')
                
                self.stdout.write(f'Successfully processed: {success_count}')
                if update_existing:
                    self.stdout.write(f'Updated existing students: {update_count}')
                self.stdout.write(f'Errors: {error_count}')
                self.stdout.write(f'Total rows processed: {success_count + update_count + error_count}')

                if error_count > 0:
                    self.stdout.write(
                        self.style.WARNING('\nSome rows had errors. Check the output above for details.')
                    )

        except UnicodeDecodeError:
            raise CommandError('File encoding error. Please save the CSV file as UTF-8.')
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {str(e)}')

    def create_parser(self, prog_name, subcommand, **kwargs):
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.add_argument(
            '--help',
            action='help',
            help='Show this help message and exit.',
        )
        return parser
