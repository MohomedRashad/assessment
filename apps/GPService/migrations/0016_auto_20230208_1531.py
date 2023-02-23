# Generated by Django 3.2.5 on 2023-02-08 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0015_merge_20230208_1521'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='availability',
            name='unique_appointment_slot',
        ),
        migrations.AlterField(
            model_name='order',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddConstraint(
            model_name='availability',
            constraint=models.UniqueConstraint(fields=('date', 'starting_time', 'ending_time', 'doctor'), name='unique_appointment_slot'),
        ),
    ]
