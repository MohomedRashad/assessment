# Generated by Django 3.2.5 on 2022-12-05 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0006_merge_20221205_1517'),
    ]

    operations = [
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='formassessmentquestion',
            name='treatment',
        ),
        migrations.AddField(
            model_name='formassessmentquestion',
            name='treatment',
            field=models.ManyToManyField(to='GPService.Treatment'),
        ),
    ]
