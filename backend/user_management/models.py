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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    expired = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # OTP expires in 10 minutes
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def expire(self):
        """Mark this OTP as expired."""
        if self.is_expired() and not self.expired:
            self.expired = True
            self.save()

    def _str_(self):
        return f"OTP for {self.user.email} - {self.code}"
        

def generate_short_uuid():
    # Generate a UUID, convert to bytes, then encode in base64, removing padding
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:16]



class User(AbstractUser):
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
    image= models.ImageField(upload_to='user_images', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    username = models.CharField(max_length=100, blank=True, null=True, unique=False)  # Make username optional
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    
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
    is_active = models.BooleanField(default=False)
    # is_user_admin = models.BooleanField(default=False)
    # is_authenticated = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'  # Use email for login instead of username
    REQUIRED_FIELDS = []  # Remove 'username' from REQUIRED_FIELDS

    objects = UserManager()

    def __str__(self):
        return self.email


class Address(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    ADDRESS_TYPE_CHOICES = [
        ('S', 'Shipping Address'),
        ('B', 'Billing Address'),
    ]
    street_address = models.CharField(max_length=100)
    street_address2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address_type}, {self.street_address}, {self.state}, {self.zip_code}"


class PhysicalAddress(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='user_address')

    full_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=100)
    street_address2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    is_default = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Physical address for - {self.full_name}:  {self.street_address}, {self.state}, {self.zip_code}"


class CreditCard(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='credit_card')
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

    def __str__(self):
        return f"Credit Card for {self.user.email} - Default: {self.is_default}"
