# Generated manually to add departure_date field

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_bus_return_dates_bus_weekend_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='departure_date',
            field=models.DateField(
                default=django.utils.timezone.now,
                help_text='Date when this bus is available for departure'
            ),
        ),
    ]
