# Generated by Django 4.2.4 on 2023-11-19 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0002_alter_fabricmaterial_fabric_inventory_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToDo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.CharField(choices=[('SEW', 'Sew the curtains'), ('PACKAGE', 'Package the order')], max_length=20)),
                ('description', models.TextField()),
                ('status', models.CharField(default='TODO', max_length=10)),
                ('comments', models.TextField(blank=True, null=True)),
            ],
        ),
    ]