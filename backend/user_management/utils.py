import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, BadHeaderError
from celery import shared_task
from google.cloud import storage
from datetime import timedelta

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def send_custom_email(subject, template_name, context, recipient_list):
    """
    Celery task to send emails asynchronously.
    """
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER

        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

        logger.info(f"✅ Email sent to {', '.join(recipient_list)} with subject: '{subject}'")
        return True

    except BadHeaderError:
        logger.error(f"❌ Invalid header in subject '{subject}'")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending email to {', '.join(recipient_list)}: {str(e)}")
        return False


def list_files(bucket_name, folder_name):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=folder_name)
    return [blob.name for blob in blobs]

def generate_signed_url(bucket_name, blob_name, expiration_minutes=10):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        expiration=timedelta(minutes=expiration_minutes),
        version='v4'
    )
    return url
