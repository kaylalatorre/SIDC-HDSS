# Generated by Django 3.2.8 on 2022-01-19 07:40

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0023_auto_20220109_1032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activities_form',
            name='act_asm',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='act_extvet',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='is_noted',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='is_reported',
        ),
        migrations.RemoveField(
            model_name='farm',
            name='farm_weight',
        ),
        migrations.RemoveField(
            model_name='farm_weight',
            name='code',
        ),
        migrations.RemoveField(
            model_name='farm_weight',
            name='is_noted',
        ),
        migrations.RemoveField(
            model_name='farm_weight',
            name='is_posted',
        ),
        migrations.RemoveField(
            model_name='farm_weight',
            name='weight_asm',
        ),
        migrations.RemoveField(
            model_name='farm_weight',
            name='weight_mgtStaff',
        ),
        migrations.RemoveField(
            model_name='farm_weight',
            name='weight_tech',
        ),
        migrations.RemoveField(
            model_name='mortality',
            name='date_approved',
        ),
        migrations.RemoveField(
            model_name='mortality',
            name='is_approved',
        ),
        migrations.RemoveField(
            model_name='mortality',
            name='last_updated',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='is_noted',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='is_posted',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='is_reported',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='mort_asm',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='mort_extvet',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='mort_mgtStaff',
        ),
        migrations.RemoveField(
            model_name='mortality_form',
            name='mort_tech',
        ),
        migrations.AddField(
            model_name='activities_form',
            name='reject_reason',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='mem_announcement',
            name='reject_reason',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='pigpen_group',
            name='date_added',
            field=models.DateField(default=django.utils.timezone.now, editable=False),
        ),
    ]