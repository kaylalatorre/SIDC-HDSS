# Generated by Django 3.2.8 on 2021-11-08 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0004_auto_20211108_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farm',
            name='extbio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farmsapp.externalbiosec'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='intbio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farmsapp.internalbiosec'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='num_pens',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]