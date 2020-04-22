# Generated by Django 3.0.5 on 2020-04-22 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='team.Team'),
        ),
        migrations.AlterField(
            model_name='team',
            name='logo',
            field=models.ImageField(upload_to='team/static/img/'),
        ),
    ]
