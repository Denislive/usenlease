# Generated by Django 4.2 on 2025-01-24 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0014_faq'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinfo',
            name='privacy_cookie_notice',
            field=models.TextField(default='Privacy and cookie Notice', verbose_name='Privacy and Cookie Notice'),
            preserve_default=False,
        ),
    ]
