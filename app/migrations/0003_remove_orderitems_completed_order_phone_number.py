# Generated by Django 5.0.4 on 2025-03-09 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_table_occupied'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitems',
            name='completed',
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
