# Generated by Django 3.2.5 on 2023-02-27 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20230224_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pharmacy',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='useremailverification',
            name='code',
            field=models.PositiveIntegerField(),
        ),
    ]
