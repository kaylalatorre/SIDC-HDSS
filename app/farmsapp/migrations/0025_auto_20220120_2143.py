# Generated by Django 3.2.8 on 2022-01-20 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0024_auto_20220119_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='activities_form',
            name='is_latest',
            field=models.BooleanField(null=True),
        ),
    ]
