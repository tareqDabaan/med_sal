# Generated by Django 4.2.6 on 2024-01-09 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_alter_service_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='discount_ammount',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]