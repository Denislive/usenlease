from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from google.cloud import storage
from datetime import timedelta
import logging
from django.core.mail import send_mail, BadHeaderError
from celery import shared_task

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def send_custom_email(subject, template_name, context, recipient_list):
    """
    Celery Task to send custom emails asynchronously.

    :param subject: Subject of the email
    :param template_name: Name of the HTML template file
    :param context: Context data to render the template
    :param recipient_list: List of recipient email addresses
    """
    try:
        # Ensure context does not contain unserializable data (like Django model instances)
        if "user" in context and hasattr(context["user"], "id"):
            context["user"] = {
                "id": context["user"].id,
                "username": context["user"].username,
                "email": context["user"].email,
                "first_name": context["user"].first_name,
                "last_name": context["user"].last_name,
            }

        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER

        # Send the email
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

        # Log success
        logger.info(f"Email sent successfully to {', '.join(recipient_list)} with subject: '{subject}'")
        return True

    except BadHeaderError:
        logger.error(f"Failed to send email: Invalid header in subject '{subject}'")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {', '.join(recipient_list)}. Error: {str(e)}")
        return False


def list_files(bucket_name, folder_name):
    """
    List all files in a folder within a Google Cloud Storage bucket.

    :param bucket_name: Name of the GCS bucket
    :param folder_name: Name of the folder in the bucket
    :return: List of file names
    """
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=folder_name)
    return [blob.name for blob in blobs]


def generate_signed_url(bucket_name, blob_name, expiration_minutes=10):
    """
    Generate a signed URL for a file in Google Cloud Storage.

    :param bucket_name: Name of the GCS bucket
    :param blob_name: Name of the file in the bucket
    :param expiration_minutes: Time in minutes for which the URL should be valid
    :return: Signed URL
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        expiration=timedelta(minutes=expiration_minutes),
        version='v4'
    )
    return url
