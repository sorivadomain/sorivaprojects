# Generated by Django 5.2.1 on 2025-05-25 09:18

import apps.academics.models
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0004_alter_result_marks'),
        ('corecode', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentInformations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discipline', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')], help_text="The student's discipline grade.", max_length=1)),
                ('sports_and_games', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')], help_text="The student's sports and games grade.", max_length=1)),
                ('collaboration', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')], help_text="The student's collaboration grade.", max_length=1)),
                ('religious', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')], help_text="The student's religious performance grade.", max_length=1)),
                ('date_of_closing', models.DateField(default=django.utils.timezone.now, help_text='The date when the term closes (defaults to today).')),
                ('date_of_opening', models.DateField(default=apps.academics.models.get_default_date_of_opening, help_text='The date when the term opens (defaults to one month after closing date).')),
                ('class_teacher_comments', models.TextField(blank=True, help_text='Comments from the class teacher.')),
                ('academic_comments', models.TextField(blank=True, help_text="Comments regarding the student's academic performance.")),
                ('headmaster_comments', models.TextField(blank=True, help_text='Comments from the headmaster.')),
                ('date_created', models.DateTimeField(auto_now_add=True, help_text='The date and time when this record was created.')),
                ('date_updated', models.DateTimeField(auto_now=True, help_text='The date and time when this record was last updated.')),
                ('exam', models.ForeignKey(help_text='The exam associated with this information.', on_delete=django.db.models.deletion.CASCADE, to='academics.exam')),
                ('session', models.ForeignKey(help_text='The academic session for this information.', on_delete=django.db.models.deletion.CASCADE, to='corecode.academicsession')),
                ('student', models.ForeignKey(help_text='The student this information belongs to.', on_delete=django.db.models.deletion.CASCADE, to='students.student')),
                ('student_class', models.ForeignKey(default=None, help_text='The class of the student for this information.', on_delete=django.db.models.deletion.CASCADE, to='corecode.studentclass')),
                ('term', models.ForeignKey(help_text='The academic term for this information.', on_delete=django.db.models.deletion.CASCADE, to='corecode.academicterm')),
            ],
            options={
                'verbose_name': 'Student Information',
                'verbose_name_plural': 'Student Informations',
                'unique_together': {('student', 'session', 'term', 'exam')},
            },
        ),
    ]
