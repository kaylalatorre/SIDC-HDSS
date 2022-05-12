# Generated by Django 4.0 on 2022-04-25 08:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0038_auto_20220425_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='disease_case',
            name='num_pigs_affect',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='disease_record',
            name='total_died',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='disease_record',
            name='total_recovered',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='farm_weight',
            name='ref_farm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.farm'),
        ),
        migrations.AddField(
            model_name='farm_weight',
            name='remarks',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='hog_raiser',
            name='mem_code',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]