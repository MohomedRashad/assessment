# Generated by Django 3.2.5 on 2022-10-26 10:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('BOOKED', 'BOOKED'), ('ONGOING', 'ONGOING'), ('COMPLETED', 'COMPLETED'), ('CANCELED', 'CANCELED')], default='BOOKED', max_length=15)),
                ('attachment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FormAssessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('ONETIMEFORM', 'ONETIMEFORM'), ('SUBSCRIPTIONFORM', 'SUBSCRIPTIONFORM')], max_length=20)),
                ('is_assessed', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('assessed_date', models.DateTimeField(null=True)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Assesses', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Takes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('LIQUID', 'LIQUID'), ('TABLET', 'TABLET'), ('CAPSULES', 'CAPSULES'), ('DROPS', 'DROPS')], max_length=50)),
                ('available_quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='TreatmentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('treatment_name', models.CharField(max_length=100)),
                ('question_title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='RecommendedVaccine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted_date', models.DateTimeField(verbose_name=django.utils.timezone.now)),
                ('Country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GPService.country')),
                ('Medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GPService.medicine')),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prescribed_quantity', models.IntegerField()),
                ('is_accepted', models.BooleanField(default=False)),
                ('appointment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='GPService.appointment')),
                ('form_assessment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='GPService.formassessment')),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GPService.medicine')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('FORMASSESSMENT', 'FORMASSESSMENT'), ('VIDEOASSESSMENT', 'VIDEOASSESSMENT'), ('PRESCRIPTION', 'PRESCRIPTION')], max_length=50)),
                ('created_date', models.DateTimeField(verbose_name=django.utils.timezone.now)),
                ('appointment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='GPService.appointment')),
                ('form_assessment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='GPService.formassessment')),
            ],
        ),
        migrations.CreateModel(
            name='FormAssessmentFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provided_feedback', models.TextField()),
                ('posted_date', models.DateField(verbose_name=django.utils.timezone.now)),
                ('form_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GPService.formassessment')),
            ],
        ),
        migrations.CreateModel(
            name='FormAssessmentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('Treatment_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GPService.treatmentquestion')),
                ('form_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GPService.formassessment')),
            ],
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('starting_time', models.TimeField(default=django.utils.timezone.now)),
                ('ending_time', models.TimeField(default=django.utils.timezone.now)),
                ('is_booked', models.BooleanField(default=False)),
                ('doctor_charge', models.IntegerField(default=1000)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='availability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GPService.availability'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
