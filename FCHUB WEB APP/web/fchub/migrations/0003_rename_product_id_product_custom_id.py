# Generated by Django 4.2.4 on 2023-10-22 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0002_product_product_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='product_id',
            new_name='custom_id',
        ),
    ]
