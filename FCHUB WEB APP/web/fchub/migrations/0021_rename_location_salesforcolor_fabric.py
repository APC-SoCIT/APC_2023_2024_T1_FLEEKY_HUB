# Generated by Django 4.2.4 on 2023-11-06 14:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0020_remove_salesforcolor_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salesforcolor',
            old_name='location',
            new_name='fabric',
        ),
    ]
