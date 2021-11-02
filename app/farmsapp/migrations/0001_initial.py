<<<<<<< HEAD
# Generated by Django 3.2.8 on 2021-11-02 07:10
=======
# Generated by Django 3.2.8 on 2021-11-01 09:51
>>>>>>> nena-backend

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
<<<<<<< HEAD
            name='Farm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_registered', models.DateField()),
                ('date_filed', models.DateField()),
                ('raiser_uname', models.CharField(max_length=50)),
                ('raiser_lname', models.CharField(max_length=50)),
                ('farmer_contact', models.CharField(max_length=50)),
                ('farmer_address', models.CharField(max_length=200)),
                ('farmer_code', models.IntegerField()),
                ('area', models.CharField(max_length=15)),
                ('user_id', models.IntegerField()),
                ('num_headsApplied', models.IntegerField()),
                ('bldg_cap', models.IntegerField()),
                ('num_pens', models.IntegerField()),
                ('directly_manage', models.BooleanField(default=False)),
                ('total_pigs', models.IntegerField()),
                ('isolation_pen', models.BooleanField(default=False)),
                ('roof_height', models.FloatField()),
                ('feed_through', models.BooleanField(default=False)),
                ('bldg_curtain', models.BooleanField(default=False)),
                ('medic_tank', models.IntegerField()),
                ('waste_mgt_septic', models.BooleanField(default=False)),
                ('waste_mgt_biogas', models.BooleanField(default=False)),
                ('waste_mgt_others', models.BooleanField(default=False)),
                ('warehouse_length', models.FloatField()),
                ('warehouse_width', models.FloatField()),
                ('road_access', models.BooleanField(default=False)),
                ('internal_bio_ID', models.IntegerField()),
                ('external_bio_ID', models.IntegerField()),
                ('est_time_complete', models.DateField()),
                ('activity_ID', models.IntegerField()),
                ('weight_record_ID', models.IntegerField()),
                ('symptoms_record_ID', models.IntegerField()),
=======
            name='ExternalBiosec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bird_proof', models.IntegerField()),
                ('perim_fence', models.IntegerField()),
                ('fiveh_m_dist', models.IntegerField()),
                ('prvdd_foot_dip', models.IntegerField()),
                ('prvdd_alco_soap', models.IntegerField()),
                ('obs_no_visitors', models.IntegerField()),
                ('prsnl_dip_footwear', models.IntegerField()),
                ('prsnl_sanit_hands', models.IntegerField()),
                ('chg_disinfect_daily', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='InternalBiosec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isol_pen', models.IntegerField()),
                ('waste_mgt', models.IntegerField()),
                ('foot_dip', models.IntegerField()),
                ('disinfect_prem', models.IntegerField()),
                ('disinfect_vet_supp', models.IntegerField()),
>>>>>>> nena-backend
            ],
        ),
    ]
