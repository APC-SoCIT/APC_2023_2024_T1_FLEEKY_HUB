# Generated by Django 4.2.4 on 2023-11-06 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0017_alter_salesforwebdata_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesforwebdata',
            name='price',
        ),
    ]
