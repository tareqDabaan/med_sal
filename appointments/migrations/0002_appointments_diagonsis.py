# Generated by Django 4.2.6 on 2024-01-18 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointments',
            name='diagonsis',
            field=models.TextField(null=True),
        ),
    ]