# Generated by Django 4.2 on 2024-11-10 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment_management', '0003_alter_cartitem_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]