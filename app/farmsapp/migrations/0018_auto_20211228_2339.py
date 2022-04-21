# Generated by Django 3.2.8 on 2021-12-28 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('farmsapp', '0017_alter_activities_form_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pigpen_Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateField(auto_now=True)),
                ('num_pens', models.IntegerField(blank=True, null=True)),
                ('total_pigs', models.IntegerField(blank=True, null=True)),
                ('final_weight', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm_weight')),
                ('ref_farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm')),
                ('start_weight', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm_weight')),
            ],
        ),
        migrations.CreateModel(
            name='Pigpen_Row',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('length', models.FloatField()),
                ('width', models.FloatField()),
                ('num_heads', models.IntegerField()),
                ('pigpen_grp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.pigpen_group')),
            ],
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='ppe_asm',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='ppe_extvet',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='ppe_tech',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='ref_farm',
        ),
        migrations.AlterField(
            model_name='activities_form',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AlterField(
            model_name='hog_symptoms',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AlterField(
            model_name='mortality_form',
            name='mort_asm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mort_asm', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mortality_form',
            name='mort_extvet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mort_extvet', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mortality_form',
            name='mort_mgtStaff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mort_mgtStaff', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mortality_form',
            name='mort_tech',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mortTech', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mortality_form',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm'),
        ),
        migrations.DeleteModel(
            name='Pigpen_Measures',
        ),
        migrations.DeleteModel(
            name='PPE_Form',
        ),
        migrations.AddField(
            model_name='hog_symptoms',
            name='pigpen_grp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.pigpen_group'),
        ),
        migrations.AddField(
            model_name='mortality_form',
            name='pigpen_grp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.pigpen_group'),
        ),
    ]
