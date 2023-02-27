# Generated by Django 3.2.5 on 2023-02-24 07:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_pharmacy_postal_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='pharmacy',
            name='name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pharmacy',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pharmacy', to=settings.AUTH_USER_MODEL),
        ),
    ]
