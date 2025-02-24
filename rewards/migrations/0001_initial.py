# Generated by Django 5.1.4 on 2025-01-22 17:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blogs', '0002_alter_blog_content'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='XamCoinSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_threshold', models.IntegerField(help_text='Time threshold in minutes')),
                ('coins_per_minute', models.IntegerField(help_text='XamCoins credited per minute after this threshold')),
            ],
        ),
        migrations.CreateModel(
            name='BlogReadingActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('last_active_time', models.DateTimeField(auto_now=True)),
                ('is_idle', models.BooleanField(default=False)),
                ('total_time_spent', models.PositiveIntegerField(default=0, help_text='Total time spent in seconds')),
                ('coins_earned', models.PositiveIntegerField(default=0, help_text='Total XamCoins earned')),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='blogs.blog')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_activities', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
