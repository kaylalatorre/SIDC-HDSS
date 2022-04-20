# Generated by Django 3.2.8 on 2021-12-15 16:34

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountData',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('data', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Activities_Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateField(blank=True, null=True)),
                ('is_checked', models.BooleanField(default=False)),
                ('is_reported', models.BooleanField(default=False)),
                ('is_noted', models.BooleanField(default=False)),
                ('act_asm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='act_asm', to=settings.AUTH_USER_MODEL)),
                ('act_extvet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='act_extvet', to=settings.AUTH_USER_MODEL)),
                ('act_liveop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='act_liveop', to=settings.AUTH_USER_MODEL)),
                ('act_tech', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='act_tech', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_name', models.CharField(blank=True, max_length=20, null=True)),
                ('tech', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tech', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalBiosec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('bird_proof', models.IntegerField(blank=True, default=1, null=True)),
                ('perim_fence', models.IntegerField(blank=True, default=1, null=True)),
                ('fiveh_m_dist', models.IntegerField(blank=True, default=1, null=True)),
                ('prvdd_foot_dip', models.IntegerField(blank=True, null=True)),
                ('prvdd_alco_soap', models.IntegerField(blank=True, null=True)),
                ('obs_no_visitors', models.IntegerField(blank=True, null=True)),
                ('prsnl_dip_footwear', models.IntegerField(blank=True, null=True)),
                ('prsnl_sanit_hands', models.IntegerField(blank=True, null=True)),
                ('chg_disinfect_daily', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_registered', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('farm_address', models.CharField(max_length=200)),
                ('loc_long', models.FloatField(blank=True, null=True)),
                ('loc_lat', models.FloatField(blank=True, null=True)),
                ('directly_manage', models.BooleanField(default=False)),
                ('wh_length', models.FloatField()),
                ('wh_width', models.FloatField()),
                ('roof_height', models.FloatField()),
                ('num_pens', models.IntegerField(blank=True, null=True)),
                ('total_pigs', models.IntegerField(blank=True, null=True)),
                ('feed_trough', models.CharField(choices=[('Semi-automatic', 'Semi-automatic'), ('Trough', 'Trough')], default='Semi-automatic', max_length=20)),
                ('bldg_cap', models.IntegerField()),
                ('bldg_curtain', models.BooleanField(default=False)),
                ('medic_tank', models.CharField(choices=[('25 GAL', '25 GAL'), ('50 GAL', '50 GAL')], default='25 GAL', max_length=10)),
                ('road_access', models.BooleanField(default=False)),
                ('is_approved', models.BooleanField(default=False)),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='area', to='farmsapp.area')),
                ('extbio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='farmsapp.externalbiosec')),
            ],
        ),
        migrations.CreateModel(
            name='Farm_Weight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_filed', models.DateField(default=django.utils.timezone.now)),
                ('is_starter', models.BooleanField(default=False)),
                ('ave_weight', models.FloatField()),
                ('total_numHeads', models.IntegerField()),
                ('total_kls', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Hog_Raiser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=50)),
                ('lname', models.CharField(max_length=50)),
                ('contact_no', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='Mortality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.IntegerField()),
                ('mortality_date', models.DateTimeField()),
                ('num_begInv', models.IntegerField()),
                ('num_today', models.IntegerField()),
                ('num_toDate', models.IntegerField()),
                ('source', models.CharField(max_length=200)),
                ('remarks', models.CharField(max_length=500)),
                ('ref_farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm')),
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
        migrations.CreateModel(
            name='PPE_Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_checked', models.BooleanField(default=False)),
                ('is_approved', models.BooleanField(default=False)),
                ('ppe_asm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppe_asm', to=settings.AUTH_USER_MODEL)),
                ('ppe_extvet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppe_extvet', to=settings.AUTH_USER_MODEL)),
                ('ppe_tech', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppe_tech', to=settings.AUTH_USER_MODEL)),
                ('ref_farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm')),
            ],
        ),
        migrations.CreateModel(
            name='Pigpen_Measures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('length', models.FloatField()),
                ('width', models.FloatField()),
                ('num_heads', models.IntegerField()),
                ('ref_farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.farm')),
            ],
        ),
        migrations.CreateModel(
            name='Mortality_Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_posted', models.BooleanField(default=False)),
                ('is_reported', models.BooleanField(default=False)),
                ('is_noted', models.BooleanField(default=False)),
                ('mort_asm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mort_asm', to=settings.AUTH_USER_MODEL)),
                ('mort_extvet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mort_extvet', to=settings.AUTH_USER_MODEL)),
                ('mort_mgtStaff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mort_mgtStaff', to=settings.AUTH_USER_MODEL)),
                ('mort_tech', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mortTech', to=settings.AUTH_USER_MODEL)),
                ('ref_mortality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.mortality')),
            ],
        ),
        migrations.CreateModel(
            name='Mem_Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('category', models.CharField(max_length=50)),
                ('recip_area', models.CharField(max_length=20)),
                ('mssg', models.CharField(max_length=500)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_approved', models.BooleanField(default=False, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InternalBiosec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('isol_pen', models.IntegerField(blank=True, default=1, null=True)),
                ('foot_dip', models.IntegerField(blank=True, default=1, null=True)),
                ('waste_mgt', models.CharField(blank=True, max_length=50, null=True)),
                ('disinfect_prem', models.IntegerField(blank=True, null=True)),
                ('disinfect_vet_supp', models.IntegerField(blank=True, null=True)),
                ('ref_farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm')),
            ],
        ),
        migrations.CreateModel(
            name='Hog_Symptoms',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_filed', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('report_status', models.CharField(default='Active', max_length=50)),
                ('num_pigs_affected', models.IntegerField(default=0)),
                ('high_fever', models.BooleanField(blank=True, default=False, null=True)),
                ('loss_appetite', models.BooleanField(blank=True, default=False, null=True)),
                ('depression', models.BooleanField(blank=True, default=False, null=True)),
                ('lethargic', models.BooleanField(blank=True, default=False, null=True)),
                ('constipation', models.BooleanField(blank=True, default=False, null=True)),
                ('vomit_diarrhea', models.BooleanField(blank=True, default=False, null=True)),
                ('colored_pigs', models.BooleanField(blank=True, default=False, null=True)),
                ('skin_lesions', models.BooleanField(blank=True, default=False, null=True)),
                ('hemorrhages', models.BooleanField(blank=True, default=False, null=True)),
                ('abn_breathing', models.BooleanField(blank=True, default=False, null=True)),
                ('discharge_eyesnose', models.BooleanField(blank=True, default=False, null=True)),
                ('death_isDays', models.BooleanField(blank=True, default=False, null=True)),
                ('death_isWeek', models.BooleanField(blank=True, default=False, null=True)),
                ('cough', models.BooleanField(blank=True, default=False, null=True)),
                ('sneeze', models.BooleanField(blank=True, default=False, null=True)),
                ('runny_nose', models.BooleanField(blank=True, default=False, null=True)),
                ('waste', models.BooleanField(blank=True, default=False, null=True)),
                ('boar_dec_libido', models.BooleanField(blank=True, default=False, null=True)),
                ('farrow_miscarriage', models.BooleanField(blank=True, default=False, null=True)),
                ('weight_loss', models.BooleanField(blank=True, default=False, null=True)),
                ('trembling', models.BooleanField(blank=True, default=False, null=True)),
                ('conjunctivitis', models.BooleanField(blank=True, default=False, null=True)),
                ('ref_farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm')),
            ],
        ),
        migrations.AddField(
            model_name='farm',
            name='farm_weight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='farmsapp.farm_weight'),
        ),
        migrations.AddField(
            model_name='farm',
            name='hog_raiser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='farmsapp.hog_raiser'),
        ),
        migrations.AddField(
            model_name='farm',
            name='intbio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='farmsapp.internalbiosec'),
        ),
        migrations.AddField(
            model_name='externalbiosec',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm'),
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('trip_type', models.CharField(choices=[('Delivery of Feeds', 'Delivery of Feeds'), ('Delivery of Medicine', 'Delivery of Medicine'), ('Delivery of Pigs', 'Delivery of Pigs'), ('Vaccinations', 'Vaccinations'), ('Inspection', 'Inspection'), ('Trucking', 'Trucking'), ('Other', 'Other')], max_length=50)),
                ('time_departure', models.TimeField()),
                ('time_arrival', models.TimeField()),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('remarks', models.CharField(blank=True, max_length=500, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('date_approved', models.DateTimeField(blank=True, null=True)),
                ('is_approved', models.BooleanField(null=True)),
                ('activity_form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.activities_form')),
                ('ref_farm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm')),
            ],
        ),
    ]
