# Generated by Django 4.2.4 on 2023-11-20 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fchub', '0003_todo'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurtainIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabric_count', models.PositiveIntegerField(default=0)),
                ('grommet_count', models.PositiveIntegerField(default=0)),
                ('rings_count', models.PositiveIntegerField(default=0)),
                ('thread_count', models.PositiveIntegerField(default=0)),
                ('length', models.PositiveIntegerField(default=0)),
                ('fabric', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fchub.fabricmaterial')),
            ],
        ),
        migrations.DeleteModel(
            name='FabricIngredient',
        ),
    ]