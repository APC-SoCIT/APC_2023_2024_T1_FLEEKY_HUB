# Generated by Django 4.2.4 on 2023-11-19 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabric', models.CharField(choices=[('Katrina', 'Katrina'), ('Blockout', 'Blockout'), ('Sheer', 'Sheer'), ('Korean', 'Korean')], max_length=250)),
                ('setType', models.CharField(choices=[('Singles', 'Singles'), ('3 in 1', '3 in 1'), ('4 in 1', '4 in 1'), ('5 in 1', '5 in 1')], max_length=250)),
                ('description', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='CleanTrainingSets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('location', models.CharField(max_length=100)),
                ('fabric', models.CharField(max_length=250)),
                ('setType', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('qty', models.PositiveIntegerField()),
                ('count', models.PositiveIntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Csv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('csv_file', models.FileField(upload_to='fchub/admin/csv/')),
                ('file_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CsvData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.CharField(max_length=20)),
                ('day', models.IntegerField()),
                ('location', models.CharField(max_length=100)),
                ('customerName', models.CharField(max_length=100)),
                ('fabric', models.CharField(max_length=100)),
                ('setType', models.CharField(max_length=20)),
                ('color', models.CharField(max_length=20)),
                ('quantity', models.IntegerField()),
                ('count', models.IntegerField()),
                ('price', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='FabricMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabric_material_id', models.CharField(blank=True, editable=False, max_length=10, unique=True)),
                ('fabric_name', models.CharField(max_length=250)),
                ('fabric', models.CharField(choices=[('Katrina', 'Katrina'), ('Blockout', 'Blockout'), ('Sheer', 'Sheer'), ('Korean', 'Korean')], max_length=250)),
                ('color', models.CharField(max_length=100)),
                ('fabric_fcount', models.PositiveIntegerField(default=0)),
                ('fabric_qty', models.PositiveIntegerField(default=0)),
                ('fabric_unit', models.CharField(max_length=250)),
                ('fabric_description', models.CharField(max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesForCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('set_tag', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='SalesForColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabric', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='SalesForFabric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('fabric', models.CharField(max_length=250)),
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
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesForWebData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabric_type', models.CharField(max_length=250, null=True)),
                ('color', models.CharField(max_length=250, null=True)),
                ('set_type', models.CharField(max_length=250, null=True)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='SuccessfulOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=100)),
                ('success_order_id', models.CharField(max_length=20, unique=True)),
                ('date', models.DateField()),
                ('location', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=250)),
                ('fabric', models.CharField(max_length=250)),
                ('setType', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('qty', models.PositiveIntegerField()),
                ('count', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Tracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabric_type', models.CharField(choices=[('Katrina', 'Katrina'), ('Blockout', 'Blockout'), ('Sheer', 'Sheer'), ('None', 'None')], max_length=250, null=True)),
                ('payment', models.CharField(choices=[('GCASH', 'GCASH'), ('CASH ON DELIVERY', 'CASH ON DELIVERY'), ('LBC', 'LBC'), ('OTHERS', 'OTHERS')], max_length=250, null=True)),
                ('price', models.PositiveIntegerField(null=True)),
                ('color', models.CharField(max_length=250, null=True)),
                ('product_tag', models.SmallIntegerField(choices=[(1, 'Blockout'), (2, '5-in-1 Katrina'), (3, '3-in-1 Katrina'), (4, 'Tieback Holder')])),
                ('setType', models.CharField(choices=[('5-in-1', '5-in-1'), ('3-in-1', '3-in-1'), ('Single', 'Single'), ('None', 'None')], max_length=250, null=True)),
                ('month_of_purchase', models.PositiveSmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], null=True)),
                ('qty', models.PositiveIntegerField(null=True)),
                ('count', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrainingSets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('location', models.CharField(max_length=100)),
                ('fabric', models.CharField(max_length=250)),
                ('setType', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=100)),
                ('qty', models.PositiveIntegerField()),
                ('count', models.PositiveIntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product_image', models.ImageField(blank=True, null=True, upload_to='customers/static/product_images')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('color', models.CharField(max_length=100)),
                ('custom_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fchub.category')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Raw Materials Thread', 'Raw Materials Thread'), ('Raw Materials Packaging', 'Raw Materials Packaging'), ('Raw Materials Attachments', 'Raw Materials Attachments')], max_length=250)),
                ('name', models.CharField(max_length=250)),
                ('count', models.PositiveIntegerField(default=0)),
                ('qty', models.PositiveIntegerField(default=0)),
                ('unit', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=250, null=True)),
                ('Custom_material_id', models.CharField(blank=True, editable=False, max_length=10, unique=True)),
            ],
            options={
                'unique_together': {('name', 'Custom_material_id')},
            },
        ),
        migrations.CreateModel(
            name='FleekyAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=50, verbose_name='Last Name')),
                ('login_time', models.DateTimeField(blank=True, null=True)),
                ('logout_time', models.DateTimeField(blank=True, null=True)),
                ('custom_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('is_customer', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Admin',
            },
        ),
    ]
