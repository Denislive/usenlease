# Generated by Django 4.2 on 2024-12-18 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0008_alter_companyinfo_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyinfo',
            old_name='terms_and_conditions',
            new_name='lesee_terms_and_conditions',
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='lessor_terms_and_conditions',
            field=models.TextField(default='something', verbose_name='Terms and Conditions'),
            preserve_default=False,
        ),
    ]
