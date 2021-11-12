# Generated by Django 3.2.8 on 2021-11-11 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('farmsapp', '0009_auto_20211111_0914'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mortality_Form',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_posted', models.BooleanField(default=False)),
                ('is_reported', models.BooleanField(default=False)),
                ('is_noted', models.BooleanField(default=False)),
                ('mort_asm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mort_asm', to='farmsapp.user')),
                ('mort_extvet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mort_extvet', to='farmsapp.user')),
                ('mort_mgtStaff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mort_mgtStaff', to='farmsapp.user')),
                ('mort_tech', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mortTech', to='farmsapp.user')),
                ('ref_mortality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='farmsapp.mortality')),
            ],
        ),
        migrations.RenameModel(
            old_name='MemAnnouncement',
            new_name='Mem_Announcement',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='actAsm',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='actExtvet',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='actLiveop',
        ),
        migrations.RemoveField(
            model_name='activities_form',
            name='actTech',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='ppeAsm',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='ppeExtvet',
        ),
        migrations.RemoveField(
            model_name='ppe_form',
            name='ppeTech',
        ),
        migrations.AddField(
            model_name='activities_form',
            name='act_asm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='act_asm', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='activities_form',
            name='act_extvet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='act_extvet', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='activities_form',
            name='act_liveop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='act_liveop', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='activities_form',
            name='act_tech',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='act_tech', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='ppe_form',
            name='ppe_asm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppe_asm', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='ppe_form',
            name='ppe_extvet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppe_extvet', to='farmsapp.user'),
        ),
        migrations.AddField(
            model_name='ppe_form',
            name='ppe_tech',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ppe_tech', to='farmsapp.user'),
        ),
        migrations.DeleteModel(
            name='MortalityForm',
        ),
    ]