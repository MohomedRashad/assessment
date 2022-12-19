# Generated by Django 3.2.5 on 2022-12-15 06:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GPService', '0011_auto_20221215_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formassessmentanswer',
            name='form_assessment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_assessment_answers', to='GPService.formassessment'),
        ),
        migrations.AlterField(
            model_name='formassessmentanswer',
            name='form_assessment_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_assessment_answers', to='GPService.formassessmentquestion'),
        ),
    ]