# Generated by Django 3.2.8 on 2022-01-05 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0020_auto_20220103_1502'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activities_form',
            name='version',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='version',
        ),
        migrations.AddField(
            model_name='farm_weight',
            name='code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='farm_weight',
            name='is_approved',
            field=models.BooleanField(null=True),
        ),
    ]
