# Generated by Django 3.2.8 on 2022-04-21 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0036_auto_20220419_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='trip_type',
            field=models.CharField(choices=[('Delivery of Veterinary Supplies', 'Delivery of Veterinary Supplies'), ('Delivery of Medicine', 'Delivery of Medicine'), ('Monthly Inventory', 'Monthly Inventory'), ('Blood Collection', 'Blood Collection'), ('Vaccinations', 'Vaccinations'), ('Inspection', 'Inspection'), ('Sold Pigs', 'Sold Pigs'), ('Other', 'Other')], max_length=50),
        ),
    ]
