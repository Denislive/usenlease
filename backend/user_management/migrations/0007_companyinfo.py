# Generated by Django 4.2 on 2024-12-17 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0006_alter_contact_email_alter_contact_message_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Company Name')),
                ('email', models.EmailField(max_length=255, verbose_name='Contact Email')),
                ('about', models.TextField(verbose_name='About Us')),
                ('terms_and_conditions', models.TextField(verbose_name='Terms and Conditions')),
                ('facebook_link', models.URLField(blank=True, null=True, verbose_name='Facebook Link')),
                ('twitter_link', models.URLField(blank=True, null=True, verbose_name='Twitter Link')),
                ('instagram_link', models.URLField(blank=True, null=True, verbose_name='Instagram Link')),
                ('linkedin_link', models.URLField(blank=True, null=True, verbose_name='LinkedIn Link')),
                ('youtube_link', models.URLField(blank=True, null=True, verbose_name='YouTube Link')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/', verbose_name='Company Logo')),
                ('address', models.CharField(blank=True, max_length=500, null=True, verbose_name='Company Address')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone Number')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Company Information',
                'verbose_name_plural': 'Company Information',
            },
        ),
    ]