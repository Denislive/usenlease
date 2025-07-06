# Standard Library Imports
import uuid
import base64
from datetime import timedelta

# Django Imports
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.utils import timezone

# Third-Party Imports
from tinymce.models import HTMLField

# Local Imports
from .managers import UserManager


class OTP(models.Model):
    """
    Represents a One-Time Password (OTP) for user authentication.

    Attributes:
        id (UUID): A unique identifier for the OTP.
        user (User): The user associated with the OTP.
        code (str): The 6-digit OTP code.
        created_at (datetime): The date and time when the OTP was created.
        expires_at (datetime): The date and time when the OTP expires.
        expired (bool): Indicates whether the OTP has expired.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    expired = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Saves the OTP instance, setting the expiration time if not already set.
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP expires in 10 minutes
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        """
        Checks if the OTP has expired.

        Returns:
            bool: True if the OTP has expired, False otherwise.
        """
        return timezone.now() > self.expires_at

    def expire(self) -> None:
        """
        Marks the OTP as expired if it has not already been marked.
        """
        if self.is_expired() and not self.expired:
            self.expired = True
            self.save()

    def __str__(self) -> str:
        """
        Returns the string representation of the OTP.

        Returns:
            str: A formatted string indicating the user and OTP code.
        """
        return f"OTP for {self.user.email} - {self.code}"


def generate_short_uuid() -> str:
    """
    Generates a shortened, URL-safe UUID using base64 encoding.

    Returns:
        str: A 16-character string representing the shortened UUID.
    """
    # Generate a UUID, convert it to bytes, encode it in URL-safe base64, and remove padding
    uuid_bytes = uuid.uuid4().bytes
    encoded_uuid = base64.urlsafe_b64encode(uuid_bytes).decode('utf-8')
    return encoded_uuid[:16]  # Return the first 16 characters


class Chat(models.Model):
    """
    Represents a chat between multiple users.

    Attributes:
        participants (QuerySet): The users participating in the chat.
        created_at (datetime): The date and time when the chat was created.
        updated_at (datetime): The date and time when the chat was last updated.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chats'
    )
    item_name = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the chat.

        Returns:
            str: A formatted string listing the participants' emails.
        """
        participant_emails = [user.email for user in self.participants.all()]
        return f"Chat between {', '.join(participant_emails)}"

    class Meta:
        ordering = ['-updated_at']  # Order chats by most recently updated
        verbose_name_plural = "chats"


class Message(models.Model):
    """
    Represents a message in a chat.

    Attributes:
        chat (Chat): The chat to which this message belongs.
        sender (User): The user who sent the message.
        receiver (User): The user who received the message.
        content (str): The text content of the message.
        sent_at (datetime): The date and time when the message was sent.
        is_deleted (bool): Indicates whether the message has been deleted.
        seen (bool): Indicates whether the message has been seen by the receiver.
        image_url (str): The URL of an image attached to the message (optional).
    """
    chat = models.ForeignKey(
        Chat,
        related_name='messages',
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # To handle deletion of messages
    seen = models.BooleanField(default=False)
    image_url = models.TextField(blank=True, null=True)  # New field to store image URL

    def __str__(self) -> str:
        """
        Returns the string representation of the message.

        Returns:
            str: A formatted string indicating the sender, receiver, and sent time.
        """
        return f"Message from {self.sender.email} to {self.receiver.email} on {self.sent_at}"

    class Meta:
        verbose_name_plural = "messages"


class User(AbstractUser):
    """
    Represents a user in the system.

    Attributes:
        id (str): A unique identifier for the user, generated using `generate_short_uuid`.
        image (ImageField): The user's profile image (optional).
        username (str): The username (optional).
        phone_number (str): The user's phone number (unique).
        email (str): The user's email address (unique).
        role (str): The user's role (lessor or lessee).
        company_name (str): The name of the user's company (optional).
        document_type (str): The type of identity document provided (e.g., ID, Passport, Driver's License).
        identity_document (FileField): The user's identity document file.
        proof_of_address (FileField): The user's proof of address file (optional).
        is_verified (bool): Indicates whether the user is verified.
        is_active (bool): Indicates whether the user account is active.
    """
    ROLE_CHOICES = [
        ('lessor', 'Lessor'),
        ('lessee', 'Lessee'),
    ]
    DOCUMENT_TYPE_CHOICES = [
        ('id', 'ID'),
        ('passport', 'Passport'),
        ('dl', 'Driver\'s License'),
    ]

    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    image = models.ImageField(
        upload_to='user_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=False  # Make username optional
    )
    phone_number = models.CharField(
        max_length=20,
        unique=True
    )
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )
    company_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        blank=True,
        null=True
    )
    identity_document = models.FileField(
        upload_to='identity_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True
    )
    proof_of_address = models.FileField(
        upload_to='proof_of_address/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'  # Use email for login instead of username
    REQUIRED_FIELDS = []  # Remove 'username' from REQUIRED_FIELDS

    objects = UserManager()

    def __str__(self) -> str:
        """
        Returns the string representation of the user.

        Returns:
            str: The user's email address.
        """
        return self.email

    class Meta:
        verbose_name_plural = "users"


class Address(models.Model):
    """
    Represents a user's address.

    Attributes:
        id (str): A unique identifier for the address, generated using `generate_short_uuid`.
        street_address (str): The primary street address.
        street_address2 (str): Additional address information (optional).
        city (str): The city of the address.
        state (str): The state or region of the address.
        zip_code (str): The postal code of the address.
        country (str): The country of the address.
        address_type (str): The type of address (e.g., Shipping, Billing).
        user (User): The user to whom this address belongs.
        is_default (bool): Indicates whether this is the user's default address.
        created_at (datetime): The date and time when the address was created.
        updated_at (datetime): The date and time when the address was last updated.
    """
    ADDRESS_TYPE_CHOICES = [
        ('S', 'Shipping Address'),
        ('B', 'Billing Address'),
    ]

    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    street_address = models.CharField(max_length=100)
    street_address2 = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the address.

        Returns:
            str: A formatted string indicating the address type, street, state, and zip code.
        """
        return f"{self.get_address_type_display()}, {self.street_address}, {self.state}, {self.zip_code}"

    class Meta:
        verbose_name_plural = "addresses"
        ordering = ['-is_default', '-created_at']  # Order by default address first, then by creation date


class PhysicalAddress(models.Model):
    """
    Represents a physical address for a user.

    Attributes:
        id (str): A unique identifier for the address, generated using `generate_short_uuid`.
        user (User): The user to whom this address belongs.
        full_name (str): The full name associated with the address.
        company_name (str): The company name associated with the address (optional).
        street_address (str): The primary street address.
        street_address2 (str): Additional address information (optional).
        city (str): The city of the address.
        state (str): The state or region of the address.
        zip_code (str): The postal code of the address.
        country (str): The country of the address.
        is_default (bool): Indicates whether this is the user's default address.
        created_at (datetime): The date and time when the address was created.
        updated_at (datetime): The date and time when the address was last updated.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='user_address'
    )
    full_name = models.CharField(max_length=100)
    company_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    street_address = models.CharField(max_length=100)
    street_address2 = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the physical address.

        Returns:
            str: A formatted string indicating the full name, street, state, and zip code.
        """
        return f"Physical address for - {self.full_name}: {self.street_address}, {self.state}, {self.zip_code}"

    class Meta:
        verbose_name_plural = "physical addresses"
        ordering = ['-is_default', '-created_at']  # Order by default address first, then by creation date


class CreditCard(models.Model):
    """
    Represents a credit card associated with a user.

    Attributes:
        id (str): A unique identifier for the credit card, generated using `generate_short_uuid`.
        user (User): The user to whom this credit card belongs.
        holder_name (str): The name of the cardholder.
        card_number (str): The credit card number.
        expiry_date (str): The expiration date of the card (format: MM/YY).
        cvc (str): The card verification code (CVC).
        bank_name (str): The name of the bank associated with the card.
        account_number (str): The bank account number.
        routing_number (str): The bank routing number.
        bank_address (str): The address of the bank.
        paypal_email (str): The PayPal email associated with the card.
        is_default (bool): Indicates whether this is the user's default credit card.
        created_at (datetime): The date and time when the credit card was added.
        updated_at (datetime): The date and time when the credit card was last updated.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='credit_cards'
    )
    holder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=19, unique=True)
    expiry_date = models.CharField(max_length=5)  # Format: MM/YY
    cvc = models.CharField(max_length=3)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    routing_number = models.CharField(max_length=9)
    bank_address = models.CharField(max_length=255)
    paypal_email = models.EmailField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the credit card.

        Returns:
            str: A formatted string indicating the user's email and whether the card is default.
        """
        return f"Credit Card for {self.user.email} - Default: {self.is_default}"

    class Meta:
        verbose_name_plural = "credit cards"
        ordering = ['-is_default', '-created_at']  # Order by default card first, then by creation date


class CompanyInfo(models.Model):
    """
    Represents company information and settings.

    Attributes:
        name (str): The name of the company.
        email (str): The contact email of the company.
        about (str): A description of the company.
        terms_and_conditions (str): The terms and conditions of the company (HTML formatted).
        privacy_cookie_notice (str): The privacy and cookie notice of the company (HTML formatted).
        facebook_link (str): The URL to the company's Facebook page (optional).
        twitter_link (str): The URL to the company's Twitter page (optional).
        instagram_link (str): The URL to the company's Instagram page (optional).
        linkedin_link (str): The URL to the company's LinkedIn page (optional).
        youtube_link (str): The URL to the company's YouTube page (optional).
        logo (ImageField): The company's logo (optional).
        address (Address): The company's physical address (optional).
        phone_number (str): The company's phone number (optional).
        created_at (datetime): The date and time when the company information was created.
        updated_at (datetime): The date and time when the company information was last updated.
    """
    name = models.CharField(
        max_length=255,
        verbose_name="Company Name"
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="Contact Email"
    )
    about = models.TextField(verbose_name="About Us")
    terms_and_conditions = HTMLField(verbose_name="Terms and Conditions")  # Uses TinyMCE in the admin
    privacy_cookie_notice = HTMLField(verbose_name="Privacy and Cookie Notice")  # Uses TinyMCE in the admin
    facebook_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Facebook Link"
    )
    twitter_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Twitter Link"
    )
    instagram_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Instagram Link"
    )
    linkedin_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="LinkedIn Link"
    )
    youtube_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="YouTube Link"
    )
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        verbose_name="Company Logo"
    )
    address = models.OneToOneField(
        Address,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Phone Number"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the company.

        Returns:
            str: The name of the company.
        """
        return self.name

    class Meta:
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"
        ordering = ['-updated_at']  # Order by most recently updated


class Contact(models.Model):
    """
    Represents a contact message from a user.

    Attributes:
        name (str): The name of the person sending the message.
        email (str): The email address of the person sending the message.
        message (str): The content of the message.
        created_at (datetime): The date and time when the message was sent.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the contact message.

        Returns:
            str: A formatted string indicating the sender's name.
        """
        return f"Message from {self.name}"

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-created_at']  # Order by most recent messages first


class FAQ(models.Model):
    """
    Represents a frequently asked question (FAQ).

    Attributes:
        question (str): The question being asked.
        answer (str): The answer to the question.
        created_at (datetime): The date and time when the FAQ was created.
        updated_at (datetime): The date and time when the FAQ was last updated.
    """
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the FAQ.

        Returns:
            str: The question being asked.
        """
        return self.question

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['created_at']  # Order FAQs by creation time