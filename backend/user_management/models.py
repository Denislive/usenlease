from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from .managers import UserManager

import uuid
import base64
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):
    # Represents a One-Time Password (OTP) for authentication or verification.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)  # 6-character OTP code.
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation.
    expires_at = models.DateTimeField()  # Expiration time for the OTP.
    expired = models.BooleanField(default=False)  # Indicates whether the OTP is expired.

    def save(self, *args, **kwargs):
        # Automatically sets an expiration time if not provided.
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP expires in 10 minutes.
        super().save(*args, **kwargs)

    def is_expired(self):
        # Checks if the OTP has expired.
        return timezone.now() > self.expires_at

    def expire(self):
        # Marks the OTP as expired if it is past its expiration time.
        if self.is_expired() and not self.expired:
            self.expired = True
            self.save()

    def _str_(self):
        # String representation of the OTP.
        return f"OTP for {self.user.email} - {self.code}"


def generate_short_uuid():
    # Generates a short, unique identifier using base64 encoding of a UUID.
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:16]


class Chat(models.Model):
    # Represents a chat conversation between users.
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for chat creation.
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update.

    def __str__(self):
        # String representation of the chat participants.
        return f"Chat between {', '.join([user.email for user in self.participants.all()])}"


class Message(models.Model):
    # Represents a message in a chat.
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()  # The content of the message.
    sent_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the message was sent.
    is_deleted = models.BooleanField(default=False)  # Indicates if the message was deleted.
    seen = models.BooleanField(default=False)  # Indicates if the message was seen.

    def __str__(self):
        # String representation of the message.
        return f"Message from {self.sender.email} to {self.receiver.email} on {self.sent_at}"


class User(AbstractUser):
    # Extends the default Django user model.
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    ROLE_CHOICES = [
        ('lessor', 'Lessor'),
        ('lessee', 'Lessee'),
    ]
    DOCUMENT_TYPE_CHOICES = [
        ('id', 'ID'),
        ('passport', 'Passport'),
        ('dl', 'Driver\'s License'),
    ]
    image = models.ImageField(
        upload_to='user_images', blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )  # Optional user profile image.
    username = models.CharField(max_length=100, blank=True, null=True, unique=False)  # Optional username.
    phone_number = models.CharField(max_length=20, unique=True)  # Unique phone number.
    email = models.EmailField(unique=True)  # Unique email address.
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  # Role of the user.
    company_name = models.CharField(max_length=150, blank=True, null=True)  # Optional company name.

    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES)  # Type of identity document.
    identity_document = models.FileField(
        upload_to='identity_documents/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )  # Uploaded identity document.

    proof_of_address = models.FileField(
        upload_to='proof_of_address/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )  # Uploaded proof of address.

    is_verified = models.BooleanField(default=False)  # Indicates if the user is verified.
    is_active = models.BooleanField(default=False)  # Indicates if the user account is active.

    USERNAME_FIELD = 'email'  # Login field for the user.
    REQUIRED_FIELDS = []  # Additional required fields.

    objects = UserManager()  # Custom manager for the User model.

    def __str__(self):
        # String representation of the user.
        return self.email


class Address(models.Model):
    # Represents an address associated with a user.
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    ADDRESS_TYPE_CHOICES = [
        ('S', 'Shipping Address'),
        ('B', 'Billing Address'),
    ]
    street_address = models.CharField(max_length=100)  # First line of the address.
    street_address2 = models.CharField(max_length=100, blank=True, null=True)  # Second line of the address.
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, blank=True, null=True)  # Address type.

    user = models.ForeignKey(User, on_delete=models.PROTECT)  # Associated user.

    is_default = models.BooleanField(default=False)  # Indicates if this is the default address.

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation.
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update.

    def __str__(self):
        # String representation of the address.
        return f"{self.address_type}, {self.street_address}, {self.state}, {self.zip_code}"


class PhysicalAddress(models.Model):
    # Represents a physical address associated with a user.
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='user_address'
    )  # Each user can have one physical address.

    full_name = models.CharField(max_length=100)  # Full name of the user.
    company_name = models.CharField(max_length=100, blank=True, null=True)  # Optional company name.
    street_address = models.CharField(max_length=100)  # First line of the address.
    street_address2 = models.CharField(max_length=100, blank=True, null=True)  # Second line of the address.
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    is_default = models.BooleanField(default=True)  # Indicates if this is the default physical address.

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation.
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update.

    def __str__(self):
        # String representation of the physical address.
        return f"Physical address for - {self.full_name}:  {self.street_address}, {self.state}, {self.zip_code}"


class CreditCard(models.Model):
    # Represents a credit card associated with a user.
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='credit_card')  # Associated user.
    holder_name = models.CharField(max_length=100)  # Name of the cardholder.
    card_number = models.CharField(max_length=19, unique=True)  # Unique credit card number.
    expiry_date = models.CharField(max_length=5)  # Expiry date in the format MM/YY.
    cvc = models.CharField(max_length=3)  # CVC code of the card.

    bank_name = models.CharField(max_length=100)  # Bank associated with the card.
    account_number = models.CharField(max_length=20)  # Bank account number.
    routing_number = models.CharField(max_length=9)  # Routing number for the bank.
    bank_address = models.CharField(max_length=255)  # Address of the bank.
    paypal_email = models.EmailField()  # PayPal email associated with the user.

    is_default = models.BooleanField(default=False)  # Indicates if this is the default credit card.

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation.
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for last update.

    def __str__(self):
        # String representation of the credit card.
        return f"Credit Card for {self.user.email} - Default: {self.is_default}"
