# Generated by Django 4.2 on 2024-12-18 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0011_rename_lesor_terms_and_conditions_companyinfo_lessor_terms_and_conditions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyinfo',
            name='lesee_terms_and_conditions',
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='lessee_terms_and_conditions',
            field=models.TextField(default='Lessee', verbose_name='Lesee Terms and Conditions'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='companyinfo',
            name='lessor_terms_and_conditions',
            field=models.TextField(verbose_name='Lessor terms and Conditions'),
        ),
    ]