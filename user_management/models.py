from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from .managers import UserManager


class User(AbstractUser):
    ROLE_CHOICES = [
        ('lessor', 'Lessor'),
        ('lessee', 'Lessee'),
    ]
    DOCUMENT_TYPE_CHOICES = [
        ('id', 'ID'),
        ('passport', 'Passport'),
        ('dl', 'Driver\'s License'),
    ]
    company_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)  # Make username optional
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES)
    identity_document = models.FileField(
        upload_to='identity_documents/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )

    proof_of_address = models.FileField(
        upload_to='proof_of_address/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    

    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'  # Use email for login instead of username
    REQUIRED_FIELDS = []  # Remove 'username' from REQUIRED_FIELDS

    objects = UserManager()

    def __str__(self):
        return self.email


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('S', 'Shipping Address'),
        ('B', 'Billing Address'),
    ]
    street_address = models.CharField(max_length=255)
    street_address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street_address}, {self.state}, {self.zip_code}"


class PhysicalAddress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='user')

    full_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    street_address = models.CharField(max_length=255)
    street_address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    is_default = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Physical - {self.full_name}, {self.street_address}, {self.state}, {self.zip_code}"


class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='credit_card')
    holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=19, blank=True, null=True, unique=True)
    expiry_date = models.CharField(max_length=5, blank=True, null=True)  # Format: MM/YY
    cvc = models.CharField(max_length=3, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    routing_number = models.CharField(max_length=9, blank=True, null=True)
    bank_address = models.CharField(max_length=255, blank=True, null=True)
    paypal_email = models.EmailField(blank=True, null=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Credit Card of {self.user.email} - Default: {self.is_default}"
