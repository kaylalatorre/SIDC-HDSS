# Generated by Django 3.2.8 on 2021-12-19 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0009_auto_20211219_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mortality',
            name='remarks',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='mortality',
            name='source',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]