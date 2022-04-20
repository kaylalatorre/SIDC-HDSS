# Generated by Django 3.2.8 on 2022-04-18 03:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0033_auto_20220416_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mortality',
            name='source',
            field=models.CharField(blank=True, choices=[('Incident Case', 'Incident Case'), ('Disease Case', 'Disease Case'), ('Unknown', 'Unknown')], default='Unknown', max_length=50, null=True),
        ),
    ]
