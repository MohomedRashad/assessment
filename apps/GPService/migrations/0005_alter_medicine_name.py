# Generated by Django 3.2.5 on 2022-11-30 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0004_alter_medicine_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicine',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
