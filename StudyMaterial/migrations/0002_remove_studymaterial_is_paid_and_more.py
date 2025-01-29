# Generated by Django 5.1.4 on 2025-01-28 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StudyMaterial', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studymaterial',
            name='is_paid',
        ),
        migrations.RemoveField(
            model_name='studymaterial',
            name='price',
        ),
        migrations.AddField(
            model_name='studymaterial',
            name='is_premium',
            field=models.BooleanField(default=False, help_text='Mark this study material as premium.'),
        ),
        migrations.AddField(
            model_name='studymaterial',
            name='unlock_cost',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Unlock cost in XamCoins or Wallet Money.', max_digits=10),
        ),
    ]
