# Generated by Django 5.1.4 on 2025-01-28 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0006_alter_xamcoinconversion_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='referralbonus',
            name='milestone',
            field=models.IntegerField(default=1, help_text='Number of referrals required for this bonus'),
        ),
    ]
