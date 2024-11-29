from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify

from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from user_management.models import Address
from datetime import datetime
import uuid
import base64
from django.db.models import Avg

def generate_short_uuid():
    # Generate a UUID, convert to bytes, then encode in base64, removing padding
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:16]



class Category(models.Model):
    # Define the primary key and unique ID for the category model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Name of the category, unique for each category
    name = models.CharField(max_length=50, unique=True)
    # Optional description for the category
    description = models.TextField(blank=True, null=True)
    # Slug field for URL-friendly category name
    slug = models.SlugField(unique=True, blank=True)
    # Parent category if this is a subcategory
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='subcategories')
    # Optional image field for the category
    image = models.ImageField(upload_to="category_images", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])  # Assuming you want to store images as URLs

    # Meta options to order categories alphabetically by name
    class Meta:
        ordering = ('name',)

    # String representation of the category instance
    def __str__(self):
        return f"parent category: {self.parent} - category: {self.name}"
    
    # Method to generate the absolute URL for the category
    def get_absolute_url(self):
        return f'/{self.slug}/'
    
    # Override the save method to auto-generate the slug if not provided
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Generate a slug from the category name
        super().save(*args, **kwargs)


class Tag(models.Model):
    # Define the primary key and unique ID for the tag model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Name of the tag, unique for each tag
    name = models.CharField(max_length=50, unique=True)

    # String representation of the tag instance
    def __str__(self):
        return self.name


class Equipment(models.Model):
    # Define the primary key and unique ID for the equipment model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Foreign key to link the equipment to the user (owner)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipments')
    # Foreign key to link the equipment to a category
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='equipments')
    # Many-to-many relation with tags to categorize equipment
    tags = models.ManyToManyField(Tag)
    # Name of the equipment
    name = models.CharField(max_length=50)
    # Detailed description of the equipment
    description = models.TextField()
    # Hourly rental rate for the equipment
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    # Address where the equipment is located
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    # Available quantity of the equipment for rent
    available_quantity = models.PositiveIntegerField(default=0)
    # Boolean to indicate if the equipment is currently available
    is_available = models.BooleanField(default=True)
    # Timestamps for creation and update of the equipment record
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    # Terms and conditions for renting the equipment
    terms = models.TextField()
    # Slug field to generate URL-friendly name for equipment
    slug = models.SlugField(unique=True, blank=True, editable=False)

    # Meta options to order equipment by the date of creation, most recent first
    class Meta:
        ordering = ('-date_created',)

    # String representation of the equipment
    def __str__(self):
        return self.name

    # Method to get the absolute URL for the equipment
    def get_absolute_url(self):
        return reverse('equipment_detail', kwargs={'slug': self.slug, 'id': self.id})

    # Method to calculate the average rating of the equipment based on reviews
    def get_average_rating(self):
        reviews = self.equipment_reviews.all()  # Get all reviews for the equipment
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']  # Calculate the average rating
            return avg_rating
        return None  # Return None if no reviews exist

    # Override the save method to auto-generate the slug and set the upload path for images
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Generate a slug from the equipment name
        self.images.field.upload_to = f'equipments/{self.category.name}/'  # Set the upload path for equipment images
        super().save(*args, **kwargs)


# Image Model
class Image(models.Model):
    # Define the primary key and unique ID for the image model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Foreign key to link the image to an equipment item
    equipment = models.ForeignKey(Equipment, related_name='images', on_delete=models.CASCADE)
    # Image file for the equipment
    image = models.ImageField(upload_to='equipment_images/')

    # String representation of the image
    def __str__(self):
        return f"Image for {self.equipment.name}"
    
    # Custom validation for the image model to ensure no more than 4 images per equipment item
    def clean(self):
        if Equipment.objects.filter(pk=self.pk).exists():
            if self.images.count() >= 4:
                raise ValidationError("An equipment item cannot have more than 4 images.")
        super().clean()

    # Property to get the image URL
    @property
    def image_url(self):
        return self.image.url

    # Meta options to ensure the combination of equipment and image ID is unique
    class Meta:
        unique_together = ('equipment', 'id')


class Specification(models.Model):
    # Define the primary key and unique ID for the specification model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Foreign key to link the specification to an equipment item
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='specifications')
    # Name of the specification (e.g., size, weight)
    name = models.CharField(max_length=255)
    # Value of the specification (e.g., "50kg", "10m")
    value = models.CharField(max_length=255)

    # String representation of the specification
    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    # Define the primary key and unique ID for the review model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Foreign key to link the review to an equipment item
    equipment = models.ForeignKey('Equipment', related_name='equipment_reviews', null=True, blank=True, on_delete=models.CASCADE)
    # Optional foreign key to link the review to the equipment owner
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner_reviews', null=True, blank=True, on_delete=models.CASCADE)
    # Foreign key to link the review to the user who submitted it
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')
    # Rating for the equipment (from 1 to 5)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    # Optional review text
    review_text = models.TextField(blank=True, null=True)
    # Timestamp for when the review was created
    date_created = models.DateTimeField(auto_now_add=True)

    # Meta options to order reviews by creation date (most recent first)
    class Meta:
        ordering = ['-date_created']

    # String representation of the review
    def __str__(self):
        if self.equipment:
            return f'Review for {self.equipment.name} by {self.user.username}'
        elif self.owner:
            return f'Review for {self.owner.username} by {self.user.username}'


class Cart(models.Model):
    # Define the primary key and unique ID for the cart model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # One-to-one relation with the user who owns the cart
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    # Total price of the cart
    cart_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Total number of items in the cart
    total_cart_items = models.IntegerField(default=0)
    # Timestamp for when the cart was created
    date_created = models.DateTimeField(auto_now_add=True)
    # Timestamp for when the cart was last updated
    date_updated = models.DateTimeField(auto_now=True)

    # String representation of the cart
    def __str__(self):
        return f"Cart {self.id}"

    # Property to calculate the total price of the cart
    @property
    def get_cart_total(self):
        if self.pk is None:
            return 0
        cart_items = self.cart_items.all()
        total = sum([item.get_cart_item_total for item in cart_items])
        return total

    # Property to calculate the total number of items in the cart
    @property
    def get_cart_items(self):
        if self.pk is None:
            return 0
        cart_items = self.cart_items.all()
        total = sum([item.quantity for item in cart_items])
        return total

    # Override the save method to update total price and item count before saving the cart
    def save(self, *args, **kwargs):
        self.cart_total_price = self.get_cart_total  # Update total price
        self.total_cart_items = self.get_cart_items  # Update total item count
        super().save(*args, **kwargs)  # Save the cart instance

class CartItem(models.Model):
    # Define the primary key and unique ID for the cart item model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Foreign key to link the cart item to a cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    # Foreign key to link the cart item to an equipment item
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    # Quantity of the item in the cart
    quantity = models.PositiveIntegerField(default=1)
    # Start date for the rental period
    start_date = models.DateField()
    # End date for the rental period
    end_date = models.DateField()
    # Boolean to indicate if the item has been ordered
    ordered = models.BooleanField(default=False)
    # Field to store the total price of this cart item
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New total field

    # String representation of the cart item (shows quantity and item name)
    def __str__(self):
        return f"{self.quantity} x {self.item.name} in cart"

    # Property to calculate the total cost for the cart item based on quantity, hourly rate, and rental duration
    @property
    def get_cart_item_total(self):
        if self.item and self.item.hourly_rate is not None:
            # Ensure start_date and end_date are datetime.date objects
            start_date = self.start_date
            end_date = self.end_date

            # Convert to date if they are in string format
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Calculate rental days
            rental_days = (end_date - start_date).days
            print("rental days", rental_days)
            if rental_days < 0:
                rental_days = 0

            # Calculate total based on hours and quantity
            total_hours = rental_days * 24
            calculated_total = self.quantity * self.item.hourly_rate * total_hours
            self.total = calculated_total  # Update the total field
            print("type of calculated total", type(calculated_total))

        return self.total if self.total else 0
    
    # Method to validate rental dates and availability of the equipment before saving the cart item
    def clean(self):
        # Validate rental dates
        if self.start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past.")
        
        if self.end_date < self.start_date:
            raise ValidationError("End date must be after the start date.")

        # Validate availability of the equipment
        if not self.item.is_available:
            raise ValidationError(f"{self.item.name} is not available for rent.")

        if self.quantity > self.item.available_quantity:
            raise ValidationError(f"Cannot add more than {self.item.available_quantity} of {self.item.name} to the cart.")

    # Save method to update total field before saving the cart item
    def save(self, *args, **kwargs):
        # Update the total field before saving
        self.total = self.get_cart_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)

        # Update the parent cart
        if self.cart:
            self.cart.save()


# Order Model
class Order(models.Model):
    # Define the primary key and unique ID for the order model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    
    # Order status choices (Pending, Approved, Rented, etc.)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rented', 'Rented'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    # Token for payment processing
    payment_token = models.CharField(max_length=255, blank=True, null=True)

    # Foreign key to link the order to a cart
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, blank=True, null=True)
    
    # Foreign key to link the order to a user (who placed the order)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    # Field to store the status of the order (pending, completed, etc.)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    # Shipping address for the order
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.PROTECT, blank=True, null=True)
    # Billing address for the order
    billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.PROTECT, blank=True, null=True)
    # Payment status (paid, pending, unpaid)
    payment_status = models.CharField(max_length=10, choices=[('paid', 'Paid'), ('pending', 'pending'), ('unpaid', 'unpaid')], default='unpaid')
    # Timestamp for when the order was created
    date_created = models.DateTimeField(auto_now_add=True)
    # Timestamp for when the order was placed (after payment)
    date_ordered = models.DateTimeField(blank=True, null=True)

    # Total price for the order
    order_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Total number of items in the order
    total_order_items = models.IntegerField(default=0)

    # Boolean to indicate if the order has been completed or not
    ordered = models.BooleanField(default=False)

    # String representation of the order (shows order ID and user)
    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    # Method to terminate the rental (change status to canceled)
    def terminate_rental(self):
        if self.status in ['pending', 'rented']:
            self.status = 'canceled'
            self.save()
        else:
            raise ValueError("Rental cannot be terminated in the current status.")

    # Method to reorder an order (only allowed for completed, returned, or canceled orders)
    def reorder(self):
        if self.status in ['completed', 'returned', 'canceled']:
            new_order = Order.objects.create(
                user=self.user,
                cart=self.cart,
                shipping_address=self.shipping_address,
                billing_address=self.billing_address,
            )
            for item in self.order_items.all():
                OrderItem.objects.create(
                    order=new_order,
                    item=item.item,
                    quantity=item.quantity,
                    start_date=item.start_date,
                    end_date=item.end_date,
                )
            return new_order
        else:
            raise ValueError("Reorder can only be performed on completed, returned, or canceled orders.")

    # Property to calculate the total price of the order
    @property
    def get_order_total(self):
        order_items = self.order_items.all()
        total = sum([item.get_order_item_total for item in order_items])
        return total

    # Property to get the total number of items in the order
    @property
    def get_order_items(self):
        order_items = self.order_items.all()
        total = sum([item.quantity for item in order_items])
        return total
    
    # Save method to update the total price and total items before saving the order
    def save(self, *args, **kwargs):
        # Update the total order price and item count before saving
        self.order_total_price = self.get_order_total  # Update total price
        self.total_order_items = self.get_order_items  # Update item count
        super().save(*args, **kwargs)  # Save the order instance
        
# OrderItem Model
class OrderItem(models.Model):
    # Define the primary key and unique ID for the order item model
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    # Boolean to indicate if the item has been ordered
    ordered = models.BooleanField(default=False)
    # Foreign key to link the order item to a specific equipment item
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    # Foreign key to link the order item to an order
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    # Quantity of the item in the order
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    # Start date for the rental period of the item
    start_date = models.DateField()
    # End date for the rental period of the item
    end_date = models.DateField()
    # Field to store the total price of this order item
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New total field

    # String representation of the order item (shows quantity and item name)
    def __str__(self):
        return f"{self.quantity} x {self.item.name} in order"

    # Property to calculate the total cost for the order item based on quantity, hourly rate, and rental duration
    @property
    def get_order_item_total(self):
        # Check if start_date and end_date are both set
        if not self.start_date or not self.end_date:
            return 0.00  # Return 0 if the dates are missing
        
        # Calculate rental days
        rental_days = (self.end_date - self.start_date).days
        if rental_days < 0:
            rental_days = 0
        # Convert rental days to total hours (assuming 24 hours per day)
        total_hours = rental_days * 24
        # Calculate the total price for the item based on quantity, hourly rate, and total hours
        return self.quantity * self.item.hourly_rate * total_hours

    # Save method to update the total field before saving the order item
    def save(self, *args, **kwargs):
        # Update the total field before saving
        self.total = self.get_order_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)

        # After saving the order item, update the associated order
        if self.order:
            self.order.save()
