# Generated by Django 3.2.5 on 2022-12-09 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0009_rename_treatment_formassessmentquestion_treatments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formassessmentfeedback',
            name='provided_feedback',
            field=models.CharField(max_length=500),
        ),
    ]
