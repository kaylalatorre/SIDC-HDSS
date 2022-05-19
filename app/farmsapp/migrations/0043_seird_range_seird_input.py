# Generated by Django 3.2.8 on 2022-05-19 04:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0042_action_recommendation_seird_range_threshold_values'),
    ]

    operations = [
        migrations.AddField(
            model_name='seird_range',
            name='seird_input',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.seird_input'),
        ),
    ]
