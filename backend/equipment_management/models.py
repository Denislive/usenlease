from datetime import datetime
import uuid
import base64
from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Avg
from decimal import Decimal
from user_management.models import Address


def generate_short_uuid():
    """Generate a shortened version of UUID using base64 encoding."""
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:16]


class Category(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to="category_images", blank=True, null=True, 
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/{self.slug}/'
    
    def save(self, *args, **kwargs):
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
    available_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    terms = models.TextField()
    slug = models.SlugField(unique=True, blank=True, editable=False)
    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('equipment_detail', kwargs={'slug': self.slug, 'id': self.id})

    def get_available_quantity(self, start_date, end_date):
        """Calculate available quantity for a given date range."""
        rented_items = CartItem.objects.filter(
            item=self,
            start_date__lt=end_date,  # Existing bookings that start before the new end_date
            end_date__gt=start_date,   # Existing bookings that end after the new start_date
            ordered=True               # Only confirmed bookings
        )

        rented_quantity = rented_items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
        available_quantity = self.available_quantity - rented_quantity
        return max(available_quantity, 0)  # Prevent negative available quantity

    def is_available_for_dates(self, start_date, end_date):
        """Check if the equipment is available for a given date range."""
        rented_items = CartItem.objects.filter(
            item=self,
            start_date__lt=end_date,
            end_date__gt=start_date,
            ordered=True
        )

        rented_quantity = rented_items.aggregate(models.Sum('quantity'))['quantity__sum'] or 0
        return self.available_quantity - rented_quantity > 0

    def get_average_rating(self):
        """Calculate the average rating of the equipment."""
        reviews = self.equipment_reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            return avg_rating
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        self.images.field.upload_to = f'equipments/{self.category.name}/'
        super().save(*args, **kwargs)





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
    review_text = models.TextField(blank=True, null=True)
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
        self.cart_total_price = self.get_cart_total  # Update total price
        self.total_cart_items = self.get_cart_items  # Update item count
        super().save(*args, **kwargs)


class CartItem(models.Model):
    id = models.CharField(
        primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    ordered = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in cart"

    @property
    def get_cart_item_total(self):
        """
        Calculate and return the total price for this cart item.
        """
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
            if rental_days < 0:
                rental_days = 0

            # Calculate total based on hours and quantity
            total_hours = rental_days * 24
            calculated_total = self.quantity * self.item.hourly_rate
            self.total = calculated_total  # Update the total field

        return self.total if self.total else 0

    def clean(self):
        """
        Validate rental dates and availability of the item in the cart.
        """
        if self.start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past.")

        if self.end_date < self.start_date:
            raise ValidationError("End date must be after the start date.")

        if not self.item.is_available:
            raise ValidationError(f"{self.item.name} is not available for rent.")

        if self.quantity > self.item.available_quantity:
            raise ValidationError(
                f"Cannot add more than {self.item.available_quantity} of {self.item.name} to the cart.")

    def save(self, *args, **kwargs):
        """
        Save the cart item, ensuring the total is calculated beforehand.
        """
        self.total = self.get_cart_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)

        # Update the parent cart
        if self.cart:
            self.cart.save()


class Order(models.Model):
    id = models.CharField(
        primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('pickup', 'Pickup Initiated'),
        ('return', 'Return Initiated'),
        ('rented', 'Rented'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
 

    payment_token = models.CharField(max_length=255, blank=True, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.PROTECT, blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.PROTECT, blank=True, null=True)
    payment_status = models.CharField(
        max_length=10, choices=[('paid', 'Paid'), ('pending', 'pending'), ('unpaid', 'unpaid')], default='unpaid')
    date_created = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(blank=True, null=True)

    order_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_order_items = models.IntegerField(default=0)
    ordered = models.BooleanField(default=False)

   
    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    def terminate_rental(self):
        """
        Terminate the rental, setting the order status to 'canceled'.
        """
        if self.status in ['pending', 'rented']:
            self.status = 'canceled'
            self.save()
        else:
            raise ValueError("Rental cannot be terminated in the current status.")

    def reorder(self):
        """
        Reorder a completed, returned, or canceled order.
        """
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

    @property
    def get_order_total(self):
        """
        Calculate the total price of the order based on the order items.
        """
        order_items = self.order_items.all()
        total = sum([item.get_order_item_total for item in order_items])
        service_fee = total * Decimal('0.06')

        return total + service_fee

    @property
    def get_order_items(self):
        """
        Calculate the total number of items in the order.
        """
        order_items = self.order_items.all()
        total = sum([item.quantity for item in order_items])
        return total

    def save(self, *args, **kwargs):
        """
        Save the order, updating the total price and item count.
        """
        self.order_total_price = self.get_order_total  # Update total price
        self.total_order_items = self.get_order_items  # Update item count
        super().save(*args, **kwargs)  # Save the order instance



class Image(models.Model):
    id = models.CharField(primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    equipment = models.ForeignKey(Equipment, related_name='images', on_delete=models.CASCADE)
    order_item = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)

    # Flags to distinguish image types
    is_pickup = models.BooleanField(default=False)  # True = Pickup image
    is_return = models.BooleanField(default=False)  # True = Return image

    image = models.ImageField(upload_to='equipment_images/')

    def __str__(self):
        category = "Pickup" if self.is_pickup else "Return" if self.is_return else "Normal"
        return f"Image for {self.equipment.name} ({category})"

    def clean(self):
        """Ensure valid image categorization and enforce limits."""
        if self.is_pickup and self.is_return:
            raise ValidationError("An image cannot be both a pickup and a return image.")

        # Count existing images by category
        pickup_count = self.equipment.images.filter(is_pickup=True).count()
        return_count = self.equipment.images.filter(is_return=True).count()
        normal_count = self.equipment.images.filter(is_pickup=False, is_return=False).count()  # Normal images

        # Enforce image limits
        if self.is_pickup and pickup_count >= 3:
            raise ValidationError("An equipment item cannot have more than 3 pickup images.")
        if self.is_return and return_count >= 3:
            raise ValidationError("An equipment item cannot have more than 3 return images.")
        if not self.is_pickup and not self.is_return and normal_count >= 4:
            raise ValidationError("An equipment item cannot have more than 4 normal images.")

        super().clean()


    @property
    def image_url(self):
        return self.image.url

    class Meta:
        unique_together = ('equipment', 'id')


class OrderItem(models.Model):
        
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('pickup', 'Pickup Initiated'),
        ('rented', 'Rented'),
        ('rejected', 'Rejected'),
        ('disputed', 'Disputed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    IDENTITY_DOCUMENT_CHOICES = [
        ('id', 'ID'),
        ('dl', 'Driver License'),
        ('passport', 'Passport'),
    ]



    id = models.CharField(
        primary_key=True, max_length=16, default=generate_short_uuid, editable=False)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

     # New fields for identity document
    identity_document_type = models.CharField(max_length=15, choices=IDENTITY_DOCUMENT_CHOICES, default=id)
    identity_document_image = models.ImageField(upload_to='pickup_identity_documents/', blank=True, null=True)
    
    return_item_condition = models.CharField(max_length=15, blank=True, null=True)
    return_item_condition_custom = models.CharField(max_length=255, blank=True, null=True)  # Custom condition description



    def __str__(self):
        return f"{self.quantity} x {self.item.name} in order"

    @property
    def get_order_item_total(self):
        """
        Calculate and return the total price for this order item.
        """
        if not self.start_date or not self.end_date:
            return 0.00  # Return 0 if the dates are missing
        
        rental_days = (self.end_date - self.start_date).days
        if rental_days < 0:
            rental_days = 0
        total_hours = rental_days * 24  # Convert rental days to total hours
        return self.quantity * self.item.hourly_rate

    def save(self, *args, **kwargs):
        """
        Save the order item, ensuring the total is calculated beforehand.
        """
        self.total = self.get_order_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)

        if self.order:
            self.order.save()
