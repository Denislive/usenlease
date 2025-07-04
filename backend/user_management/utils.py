import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, BadHeaderError, get_connection
from smtplib import SMTPServerDisconnected, SMTPConnectError
from celery import shared_task
from datetime import timedelta
from google.cloud import storage

#Set up logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5)
def send_custom_email(self, subject, template_name, context, recipient_list):
    """
    Celery task to send emails asynchronously with retries and connection pooling.
    """
    try:
        # Render the HTML and plain text email content
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER

        # Use SMTP connection pooling
        connection = get_connection(fail_silently=False)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            connection=connection
        )

        logger.info(f"✅ Email sent to {', '.join(recipient_list)} with subject: '{subject}'")
        return True

    except BadHeaderError:
        logger.error(f"❌ Invalid header in subject '{subject}'")
        return False

    except (SMTPServerDisconnected, SMTPConnectError) as e:
        delay = 2 ** self.request.retries  # exponential backoff: 2, 4, 8, 16, 32...
        logger.warning(f"⚠️ SMTP error: {str(e)} — retrying in {delay} seconds...")
        raise self.retry(exc=e, countdown=delay)

    except Exception as e:
        logger.exception(f"❌ Unexpected error sending email to {', '.join(recipient_list)}: {str(e)}")
        raise self.retry(exc=e, countdown=10)


def list_files(bucket_name, folder_name):
    """
    Lists files in a Google Cloud Storage bucket under a specific folder.
    """
    try:
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(bucket_name, prefix=folder_name)
        file_list = [blob.name for blob in blobs]
        logger.info(f"📂 Found {len(file_list)} files in '{folder_name}' folder of '{bucket_name}' bucket.")
        return file_list
    except Exception as e:
        logger.error(f"❌ Error listing files in bucket '{bucket_name}': {str(e)}")
        return []


def generate_signed_url(bucket_name, blob_name, expiration_minutes=10):
    """
    Generates a signed URL for a file in Google Cloud Storage.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            expiration=timedelta(minutes=expiration_minutes),
            version='v4'
        )
        logger.info(f"🔗 Signed URL generated for '{blob_name}': {url}")
        return url
    except Exception as e:
        logger.error(f"❌ Error generating signed URL for '{blob_name}': {str(e)}")
        return None
