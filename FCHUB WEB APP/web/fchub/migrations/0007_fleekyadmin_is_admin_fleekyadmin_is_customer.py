# Generated by Django 4.2.4 on 2023-10-24 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0006_fleekyadmin_custom_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='fleekyadmin',
            name='is_admin',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='fleekyadmin',
            name='is_customer',
            field=models.BooleanField(default=False),
        ),
    ]