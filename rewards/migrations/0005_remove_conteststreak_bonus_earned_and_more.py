# Generated by Django 5.1.4 on 2025-01-28 08:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0004_conteststreakreward'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conteststreak',
            name='bonus_earned',
        ),
        migrations.AddField(
            model_name='conteststreak',
            name='total_xamcoins_collected',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total XamCoins collected during the streak', max_digits=10),
        ),
        migrations.AddField(
            model_name='conteststreakreward',
            name='bonus_percentage',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Bonus percentage for settlement on this day', max_digits=5),
        ),
        migrations.CreateModel(
            name='LockedXamCoins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_locked', models.DecimalField(decimal_places=2, default=0.0, help_text='Total locked XamCoins from the streak', max_digits=10)),
                ('last_settlement_day', models.PositiveIntegerField(blank=True, help_text='Last settlement day reached', null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='locked_xamcoins', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
