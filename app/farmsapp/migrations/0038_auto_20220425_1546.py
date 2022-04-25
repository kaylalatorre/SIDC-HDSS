# Generated by Django 3.2.8 on 2022-04-25 07:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0037_auto_20220421_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='disease_case',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='disease_case',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Disease_Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_filed', models.DateTimeField()),
                ('num_recovered', models.IntegerField(blank=True, null=True)),
                ('num_died', models.IntegerField(blank=True, null=True)),
                ('ref_disease_case', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='farmsapp.disease_case')),
            ],
        ),
    ]
