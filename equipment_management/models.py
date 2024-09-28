from django.db import models
from django.conf import settings
from django.utils import timezone
from user_management.models import PhysicalAddress, Address
from django.contrib.sessions.models import Session
from django.shortcuts import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipments')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='equipments')
    tags = models.ManyToManyField(Tag)
    name = models.CharField(max_length=255)
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
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
        super().save(*args, **kwargs)


class Review(models.Model):
    equipment = models.ForeignKey('Equipment', related_name='reviews', null=True, blank=True, on_delete=models.CASCADE)
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


# Image Model
class Image(models.Model):
    equipment = models.ForeignKey(Equipment, related_name='images', on_delete=models.PROTECT)
    image = models.ImageField(upload_to='equipment_images/')

    def __str__(self):
        return f"Image for {self.equipment.name}"

    @property
    def image_url(self):
        return self.image.url

    class Meta:
        unique_together = ('equipment', 'id')


# Cart Model
class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)  # Use session key as a CharField
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"

    @property
    def get_cart_total(self):
        cart_items = self.cart_items.all()
        total = sum([item.get_total for item in cart_items])
        return total

    @property
    def get_cart_items(self):
        cart_items = self.cart_items.all()
        total = sum([item.quantity for item in cart_items])
        return total


# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in cart"

    @property
    def get_total(self):
        rental_days = (self.end_date - self.start_date).days
        if rental_days < 0:
            rental_days = 0
        total_hours = rental_days * 24
        return self.quantity * self.item.hourly_rate * total_hours


# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    payment_token = models.CharField(max_length=255, blank=True, null=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.CASCADE, blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', on_delete=models.CASCADE, blank=True, null=True)
    payment_status = models.CharField(max_length=10, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    date_created = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    @property
    def get_total(self):
        order_items = self.order_items.all()
        total = sum([item.get_total for item in order_items])
        return total

    @property
    def get_cart_items(self):
        order_items = self.order_items.all()
        total = sum([item.quantity for item in order_items])
        return total


# OrderItem Model
class OrderItem(models.Model):
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in order"

    @property
    def get_total(self):
        rental_days = (self.end_date - self.start_date).days
        if rental_days < 0:
            rental_days = 0
        total_hours = rental_days * 24
        return self.quantity * self.item.hourly_rate * total_hours