# Generated by Django 3.2.20 on 2023-10-01 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20231001_2010'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='measure',
            new_name='measurement_unit',
        ),
    ]
