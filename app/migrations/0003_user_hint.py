# Generated by Django 5.0.4 on 2025-03-10 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_hotel_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hint',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
