# Generated by Django 4.2.4 on 2023-10-30 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0015_alter_csv_csv_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='csv',
            name='file_name',
            field=models.CharField(default=0.00020596473883671115, max_length=255),
            preserve_default=False,
        ),
    ]
