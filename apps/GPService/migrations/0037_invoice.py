# Generated by Django 3.2.5 on 2023-06-23 07:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0036_alter_medicine_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=20, unique=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('invoice', models.TextField()),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='GPService.order')),
            ],
        ),
    ]