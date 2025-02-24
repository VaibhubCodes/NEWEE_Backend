# Generated by Django 5.1.4 on 2025-01-28 15:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('questions', '0002_remove_question_options_question_image_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MentorshipSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_per_question', models.DecimalField(decimal_places=2, default=10.0, help_text='XamCoins required per question.', max_digits=10)),
                ('max_cost_30_minutes', models.DecimalField(decimal_places=2, default=50.0, help_text='Maximum XamCoins for a 30-minute mentorship session.', max_digits=10)),
                ('max_cost_60_minutes', models.DecimalField(decimal_places=2, default=100.0, help_text='Maximum XamCoins for a 60-minute mentorship session.', max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='MentorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(help_text='Start time of availability.')),
                ('end_time', models.DateTimeField(help_text='End time of availability.')),
                ('is_booked', models.BooleanField(default=False, help_text='Is this time slot booked?')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_availability', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MentorshipSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('duration_minutes', models.PositiveIntegerField(choices=[(30, '30 minutes'), (60, '60 minutes')])),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_sessions', to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='The question content.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('answered', models.BooleanField(default=False)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_questions', to='questions.subject')),
            ],
        ),
    ]
