# Generated by Django 3.2.5 on 2022-12-12 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0005_alter_medicine_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]