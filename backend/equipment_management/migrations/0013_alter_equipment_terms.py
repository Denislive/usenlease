# Generated by Django 4.2 on 2024-12-28 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment_management', '0012_alter_equipment_terms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='terms',
            field=models.TextField(blank=True, null=True),
        ),
    ]
