# Generated by Django 3.2.5 on 2022-11-28 11:53

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('BOOKED', 'BOOKED'), ('ONGOING', 'ONGOING'), ('COMPLETED', 'COMPLETED'), ('CANCELED', 'CANCELED')], default='BOOKED', max_length=15)),
                ('attachment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='files.file')),
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
                ('type', models.CharField(choices=[('ONE_TIME_FORM', 'ONE_TIME_FORM'), ('SUBSCRIPTION_FORM', 'SUBSCRIPTION_FORM')], max_length=20)),
                ('is_assessed', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('assessed_date', models.DateTimeField(null=True)),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doctor_formassessments', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='patient_formassessments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FormAssessmentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('treatment', models.CharField(choices=[('CANCER', 'CANCER'), ('ALLERGIES', 'ALLERGIES')], max_length=100)),
                ('question', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('TABLET', 'TABLET'), ('CAPSULES', 'CAPSULES'), ('VACCINE', 'VACCINE')], max_length=50)),
                ('available_quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='RecommendedVaccine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted_date', models.DateTimeField(verbose_name=django.utils.timezone.now)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommended_vaccines', to='GPService.country')),
                ('medicine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommended_vaccines', to='GPService.medicine')),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prescribed_quantity', models.IntegerField()),
                ('is_accepted', models.BooleanField(default=False)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='GPService.appointment')),
                ('form_assessment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='GPService.formassessment')),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='GPService.medicine')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('FORM_ASSESSMENT', 'FORM_ASSESSMENT'), ('VIDEO_ASSESSMENT', 'VIDEO_ASSESSMENT'), ('PRESCRIPTION', 'PRESCRIPTION')], max_length=50)),
                ('created_date', models.DateTimeField(verbose_name=django.utils.timezone.now)),
                ('total_amount', models.IntegerField(blank=True, null=True)),
                ('appointment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='GPService.appointment')),
                ('form_assessment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='GPService.formassessment')),
            ],
        ),
        migrations.CreateModel(
            name='FormAssessmentFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provided_feedback', models.TextField()),
                ('posted_date', models.DateField(verbose_name=django.utils.timezone.now)),
                ('form_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_assessment_feedback', to='GPService.formassessment')),
            ],
        ),
        migrations.CreateModel(
            name='FormAssessmentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('form_assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_assessment_answers', to='GPService.formassessment')),
                ('form_assessment_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_assessment_answers', to='GPService.formassessmentquestion')),
            ],
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now, validators=[django.core.validators.MinValueValidator(limit_value=datetime.date.today)])),
                ('starting_time', models.TimeField()),
                ('ending_time', models.TimeField()),
                ('is_booked', models.BooleanField(default=False)),
                ('doctor_charge', models.PositiveIntegerField(default=100)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='availability',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='GPService.availability'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='availability',
            constraint=models.UniqueConstraint(fields=('starting_time', 'ending_time', 'doctor'), name='unique_appointment_slot'),
        ),
        migrations.AddConstraint(
            model_name='appointment',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'CANCELED'), _negated=True), fields=('patient', 'availability'), name='unique_appointment'),
        ),
    ]
