# Generated by Django 4.2.4 on 2023-10-22 00:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_address_customer_alter_customer_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_addresses', to='customer.address'),
        ),
    ]