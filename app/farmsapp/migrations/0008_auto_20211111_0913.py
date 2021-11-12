# Generated by Django 3.2.8 on 2021-11-11 09:13

import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('farmsapp', '0007_alter_pigpen_measures_farm'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=50)),
                ('recip_area', models.CharField(max_length=20)),
                ('mssg', models.CharField(max_length=500)),
                ('author_ID', models.CharField(max_length=30)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='asm_ID',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='extvet_ID',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='farm',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='liveop_ID',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='tech_ID',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='delivery',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='farm',
        ),
        migrations.RemoveField(
            model_name='farm',
            name='est_time_complete',
        ),
        migrations.RemoveField(
            model_name='mortality',
            name='farm',
        ),
        migrations.RemoveField(
            model_name='pigpen_measures',
            name='farm',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='approve_asm_ID',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='extvet_ID',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='farm',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='tech_ID',
        ),
        migrations.AddField(
            model_name='activities_form',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AddField(
            model_name='activity',
            name='ref_delivery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.delivery'),
        ),
        migrations.AddField(
            model_name='activity',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AddField(
            model_name='externalbiosec',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AddField(
            model_name='internalbiosec',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AddField(
            model_name='mortality',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AddField(
            model_name='pigpen_measures',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AddField(
            model_name='ppe_form',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='farm_symptoms',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='farmsapp.farm_symptoms'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='farm_weight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='farmsapp.farm_weight'),
        ),
        migrations.CreateModel(
            name='MortalityForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_posted', models.BooleanField(default=False)),
                ('is_reported', models.BooleanField(default=False)),
                ('is_noted', models.BooleanField(default=False)),
                ('mortAsm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mortAsm', to='farmsapp.user')),
                ('mortExtvet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mortExtvet', to='farmsapp.user')),
                ('mortMgtStaff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mortMgtStaff', to='farmsapp.user')),
                ('mortTech', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mortTech', to='farmsapp.user')),
                ('ref_mortality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.mortality')),
            ],
        ),
        migrations.AddField(
            model_name='activities_form',
            name='actAsm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actAsm', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='activities_form',
            name='actExtvet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actExtvet', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='activities_form',
            name='actLiveop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actLiveop', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='activities_form',
            name='actTech',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='actTech', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='ppe_form',
            name='ppeAsm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppeAsm', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='ppe_form',
            name='ppeExtvet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppeExtvet', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='ppe_form',
            name='ppeTech',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppeTech', to='farmsapp.user'),
        ),
    ]
