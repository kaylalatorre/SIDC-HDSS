# Generated by Django 3.2.8 on 2021-12-27 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0014_auto_20211227_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activities_form',
            name='version',
            field=models.IntegerField(),
        ),
    ]