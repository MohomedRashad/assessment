# Generated by Django 3.2.5 on 2023-06-21 05:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_patient_pharmacy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='pharmacy',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pharmacy', to='users.pharmacy'),
        ),
    ]
