# utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_custom_email(subject, template_name, context, recipient_list):
    """
    Function to send custom emails.

    :param subject: Subject of the email
    :param template_name: Name of the HTML template file
    :param context: Context data to render the template
    :param recipient_list: List of recipient email addresses
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = 'your_email@gmail.com'

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
