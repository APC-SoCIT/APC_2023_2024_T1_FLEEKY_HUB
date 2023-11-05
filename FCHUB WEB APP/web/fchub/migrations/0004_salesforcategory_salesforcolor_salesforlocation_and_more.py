# Generated by Django 4.2.4 on 2023-11-05 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0003_csvdata_fabric'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesForCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('set_tag', models.CharField(max_length=250)),
                ('generated_id', models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesForColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('generated_id', models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesForLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('fabric', models.CharField(max_length=250)),
                ('set_type', models.CharField(max_length=250)),
                ('location', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('generated_id', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesForProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fabric', models.CharField(max_length=3)),
                ('set_type', models.CharField(max_length=3)),
                ('generated_id', models.CharField(max_length=12, unique=True)),
            ],
        ),
    ]
