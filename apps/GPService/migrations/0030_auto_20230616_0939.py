# Generated by Django 3.2.5 on 2023-06-16 04:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0029_auto_20230615_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formassessment',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='formassessment',
            name='patient',
        ),
    ]