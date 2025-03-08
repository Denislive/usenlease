import logging
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail, BadHeaderError, get_connection
from celery import shared_task
from celery.exceptions import Retry
from google.cloud import storage
from datetime import timedelta

# Set up logging
logger = logging.getLogger(__name__)

@shared_task(
    autoretry_for=(Exception,),  # Retry for any exception
    retry_kwargs={'max_retries': 3, 'countdown': 60},  # Retry 3 times with a 60-second delay
    retry_backoff=True  # Enable exponential backoff
)
def send_custom_email(subject, template_name, context, recipient_list):
    """
    Celery task to send emails asynchronously with retries.
    """
    connection = None
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER

        # Use a persistent SMTP connection
        connection = get_connection(fail_silently=False)
        connection.open()  # Open the connection

        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_message,
            connection=connection  # Reuse the same connection
        )

        logger.info(f"✅ Email sent to {', '.join(recipient_list)} with subject: '{subject}'")
        return True

    except BadHeaderError:
        logger.error(f"❌ Invalid header in subject '{subject}'")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending email to {', '.join(recipient_list)}: {str(e)}")
        raise Retry(exc=e)  # Retry the task
    finally:
        if connection:
            connection.close()  # Close the connection after use

def list_files(bucket_name, folder_name):
    """
    List files in a GCS bucket folder.
    """
    try:
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(bucket_name, prefix=folder_name)
        return [blob.name for blob in blobs]
    except Exception as e:
        logger.error(f"❌ Error listing files in bucket '{bucket_name}' folder '{folder_name}': {str(e)}")
        return []

def generate_signed_url(bucket_name, blob_name, expiration_minutes=10):
    """
    Generate a signed URL for a GCS blob.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            expiration=timedelta(minutes=expiration_minutes),
            version='v4'
        )
        return url
    except Exception as e:
        logger.error(f"❌ Error generating signed URL for blob '{blob_name}' in bucket '{bucket_name}': {str(e)}")
        return None