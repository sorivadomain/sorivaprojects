# Generated by Django 5.2.1 on 2025-06-06 04:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentsAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_message', models.TextField(blank=True, help_text='The text content of the answer.')),
                ('audio_answer', models.FileField(blank=True, help_text='An optional audio file for the answer.', null=True, upload_to='accounts/comments/answers/audio/')),
                ('is_read', models.BooleanField(default=False, help_text='Indicates whether the answer has been read.')),
                ('date_created', models.DateTimeField(auto_now_add=True, help_text='The date and time when the answer was created.')),
                ('date_updated', models.DateTimeField(auto_now=True, help_text='The date and time when the answer was last updated.')),
                ('comment', models.ForeignKey(help_text='The comment this answer is responding to.', on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='accounts.comments')),
            ],
            options={
                'verbose_name': 'Comment Answer',
                'verbose_name_plural': 'Comment Answers',
                'ordering': ['-date_created'],
            },
        ),
    ]
