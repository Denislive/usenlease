from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify

from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from user_management.models import Address

import uuid
import base64

def generate_short_uuid():
    # Generate a UUID, convert to bytes, then encode in base64, removing padding
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:16]



class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to="category_images", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])  # Assuming you want to store images as URLs


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"parent category: {self.parent} - category: {self.name}"
    

    def get_absolute_url(self):
        return f'/{self.slug}/'
    
    def save(self, *args, **kwargs):
        # Generate slug if it is not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipments')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='equipments')
    tags = models.ManyToManyField(Tag)
    name = models.CharField(max_length=50)
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    available_quantity = models.PositiveIntegerField(default=0)  # Track the available quantity
    is_available = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    terms = models.TextField()
    slug = models.SlugField(unique=True, blank=True, editable=False)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('equipment_detail', kwargs={'slug': self.slug, 'id': self.id})

    def get_add_to_cart_url(self):
        return reverse('add-to-cart', kwargs={'slug': self.slug, 'id': self.id})

    def get_remove_from_cart_url(self):
        return reverse('remove-from-cart', kwargs={'slug': self.slug, 'id': self.id})
        

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        self.images.field.upload_to = f'equipments/{self.category.name}/'
        super().save(*args, **kwargs)


# Image Model
class Image(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    equipment = models.ForeignKey(Equipment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='equipment_images/')

    def __str__(self):
        return f"Image for {self.equipment.name}"
    
    def clean(self):
        # Ensure the instance has been saved or exists in the database
        if Equipment.objects.filter(pk=self.pk).exists():
            # Now it's safe to check related images
            if self.images.count() >= 4:
                raise ValidationError("An equipment item cannot have more than 4 images.")
        else:
            # Skipping validation for unsaved instances
            pass
        
        # Always call the parent class's clean method
        super().clean()

    @property
    def image_url(self):
        return self.image.url

    class Meta:
        unique_together = ('equipment', 'id')


        
class Specification(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    equipment = models.ForeignKey('Equipment', related_name='equipment_reviews', null=True, blank=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner_reviews', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')

    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Ratings from 1 to 5
    review_text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        if self.equipment:
            return f'Review for {self.equipment.name} by {self.user.username}'
        elif self.owner:
            return f'Review for {self.owner.username} by {self.user.username}'


class Cart(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    cart_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_cart_items = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def get_cart_total(self):
        if self.pk is None:  # Check if the instance has been saved
            return 0
        cart_items = self.cart_items.all()
        total = sum([item.get_cart_item_total for item in cart_items])  # Call get_total() as a method
        return total

    @property
    def get_cart_items(self):
        if self.pk is None:
            return 0
        cart_items = self.cart_items.all()
        total = sum([item.quantity for item in cart_items])
        return total

    def save(self, *args, **kwargs):
        # Update cart_total_price and total_cart_items before saving
        self.cart_total_price = self.get_cart_total  # Update total price
        self.total_cart_items = self.get_cart_items  # Update item count
        super().save(*args, **kwargs)  # Save the cart instance

class CartItem(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    ordered = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New total field

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in cart"

    @property
    def get_cart_item_total(self):
        if self.item and self.item.hourly_rate is not None:
            rental_days = (self.end_date - self.start_date).days
            if rental_days < 0:
                rental_days = 0
            total_hours = rental_days * 24
            calculated_total = self.quantity * self.item.hourly_rate * total_hours
            self.total = calculated_total  # Update the total field
        return 0
    
    def clean(self):
        # Validate rental dates
        if self.start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past.")
        
        if self.end_date < self.start_date:
            raise ValidationError("End date must be after the start date.")

        # Validate availability
        if not self.item.is_available:
            raise ValidationError(f"{self.item.name} is not available for rent.")

        if self.quantity > self.item.available_quantity:
            raise ValidationError(f"Cannot add more than {self.item.available_quantity} of {self.item.name} to the cart.")

    def save(self, *args, **kwargs):
        # Update the total field before saving
        self.total = self.get_cart_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)


# Order Model
class Order(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rented', 'Rented'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    payment_token = models.CharField(max_length=255, blank=True, null=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.PROTECT, blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.PROTECT, blank=True, null=True)
    payment_status = models.CharField(max_length=10, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    date_created = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(blank=True, null=True)

    order_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_order_items = models.IntegerField(default=0)

    ordered = models.BooleanField(default=False)



    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    @property
    def get_order_total(self):
        order_items = self.order_items.all()
        total = sum([item.get_order_item_total for item in order_items])
        return total

    @property
    def get_order_items(self):
        order_items = self.order_items.all()
        total = sum([item.quantity for item in order_items])
        return total
    
    def save(self, *args, **kwargs):
        # Update cart_total_price and total_cart_items before saving
        self.order_total_price = self.get_order_total  # Update total price
        self.total_order_items = self.get_order_items  # Update item count
        super().save(*args, **kwargs)  # Save the cart instance


# OrderItem Model
class OrderItem(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New total field


    def __str__(self):
        return f"{self.quantity} x {self.item.name} in order"

    @property
    def get_order_item_total(self):
        rental_days = (self.end_date - self.start_date).days
        if rental_days < 0:
            rental_days = 0
        total_hours = rental_days * 24
        return self.quantity * self.item.hourly_rate * total_hours
    
    def save(self, *args, **kwargs):
        # Update the total field before saving
        self.total = self.get_order_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)