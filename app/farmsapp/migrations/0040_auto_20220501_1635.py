# Generated by Django 3.2.8 on 2022-05-01 08:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0039_disease_case_num_pigs_affect_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pigpen_group',
            name='final_weight',
        ),
        migrations.RemoveField(
            model_name='pigpen_group',
            name='start_weight',
        ),
        migrations.AddField(
            model_name='farm_weight',
            name='pigpen_grp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.pigpen_group'),
        ),
    ]
