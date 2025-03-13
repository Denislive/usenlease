# Standard Library Imports
from datetime import datetime
import uuid
import base64
from decimal import Decimal

# Third-Party Library Imports
# (None in this case)

# Django Imports
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Avg

# Local Imports
from user_management.models import Address



def generate_short_uuid() -> str:
    """
    Generate a shortened version of UUID using base64 encoding.

    Returns:
        str: A 16-character string representing the shortened UUID.
    """
    uuid_bytes = uuid.uuid4().bytes
    encoded_uuid = base64.urlsafe_b64encode(uuid_bytes).decode('utf-8')
    return encoded_uuid[:16]


class Category(models.Model):
    """
    Represents a category in the system.

    Attributes:
        id (str): A unique identifier for the category, generated using `generate_short_uuid`.
        name (str): The name of the category (unique).
        description (str): Optional description of the category.
        slug (str): A URL-friendly slug for the category (unique).
        parent (Category): Optional parent category for creating hierarchical structures.
        image (ImageField): Optional image for the category, with allowed extensions (jpg, jpeg, png).
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    name = models.CharField(
        max_length=50,
        unique=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    image = models.ImageField(
        upload_to="category_images",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        """
        Returns the string representation of the category (its name).

        Returns:
            str: The name of the category.
        """
        return self.name

    def get_absolute_url(self) -> str:
        """
        Returns the absolute URL for the category detail page.

        Returns:
            str: The URL path for the category.
        """
        return f'/{self.slug}/'

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically generate a slug if not provided.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


from django.db import models


class Tag(models.Model):
    """
    Represents a tag in the system.

    Attributes:
        id (str): A unique identifier for the tag, generated using `generate_short_uuid`.
        name (str): The name of the tag (unique).
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self) -> str:
        """
        Returns the string representation of the tag (its name).

        Returns:
            str: The name of the tag.
        """
        return self.name


class Equipment(models.Model):
    """
    Represents an equipment item in the system.

    Attributes:
        id (str): A unique identifier for the equipment, generated using `generate_short_uuid`.
        owner (User): The user who owns the equipment.
        category (Category): The category to which the equipment belongs.
        tags (QuerySet): Tags associated with the equipment.
        name (str): The name of the equipment.
        description (str): A detailed description of the equipment.
        hourly_rate (Decimal): The hourly rental rate of the equipment.
        address (Address): The address where the equipment is located.
        available_quantity (int): The quantity of the equipment available for rent.
        is_available (bool): Indicates whether the equipment is available for rent.
        date_created (datetime): The date and time when the equipment was created.
        date_updated (datetime): The date and time when the equipment was last updated.
        terms (str): Rental terms and conditions for the equipment.
        slug (str): A URL-friendly slug for the equipment (unique).
        is_trending (bool): Indicates whether the equipment is trending.
        is_featured (bool): Indicates whether the equipment is featured.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='equipments'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='equipments'
    )
    tags = models.ManyToManyField(Tag)
    name = models.CharField(max_length=50)
    description = models.TextField()
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
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
        verbose_name_plural = "equipment"

    def __str__(self) -> str:
        """
        Returns the string representation of the equipment (its name).

        Returns:
            str: The name of the equipment.
        """
        return self.name

    def get_absolute_url(self) -> str:
        """
        Returns the absolute URL for the equipment detail page.

        Returns:
            str: The URL path for the equipment.
        """
        return reverse('equipment_detail', kwargs={'slug': self.slug, 'id': self.id})

    def get_available_quantity(self, start_date, end_date) -> int:
        """
        Calculate the available quantity of the equipment for a given date range.

        Args:
            start_date (datetime): The start date of the rental period.
            end_date (datetime): The end date of the rental period.

        Returns:
            int: The available quantity of the equipment.
        """
        rented_items = CartItem.objects.filter(
            item=self,
            start_date__lt=end_date,
            end_date__gt=start_date,
            ordered=True
        )

        rented_quantity = rented_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        available_quantity = self.available_quantity - rented_quantity
        return max(available_quantity, 0)  # Prevent negative available quantity

    def is_available_for_dates(self, start_date, end_date) -> bool:
        """
        Check if the equipment is available for a given date range.

        Args:
            start_date (datetime): The start date of the rental period.
            end_date (datetime): The end date of the rental period.

        Returns:
            bool: True if the equipment is available, False otherwise.
        """
        rented_items = CartItem.objects.filter(
            item=self,
            start_date__lt=end_date,
            end_date__gt=start_date,
            ordered=True
        )

        rented_quantity = rented_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return self.available_quantity - rented_quantity > 0

    def get_average_rating(self) -> float:
        """
        Calculate the average rating of the equipment based on reviews.

        Returns:
            float: The average rating of the equipment, or None if no reviews exist.
        """
        reviews = self.equipment_reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            return avg_rating
        return None

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically generate a slug if not provided.
        Also sets the upload path for equipment images based on the category.
        """
        if not self.slug:
            self.slug = slugify(self.name)

        self.images.field.upload_to = f'equipments/{self.category.name}/'
        super().save(*args, **kwargs)



class Specification(models.Model):
    """
    Represents a specification for an equipment item.

    Attributes:
        id (str): A unique identifier for the specification, generated using `generate_short_uuid`.
        equipment (Equipment): The equipment to which this specification belongs.
        name (str): The name of the specification.
        value (str): The value of the specification.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='specifications'
    )
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self) -> str:
        """
        Returns the string representation of the specification (name: value).

        Returns:
            str: The formatted string representation of the specification.
        """
        return f"{self.name}: {self.value}"


class Review(models.Model):
    """
    Represents a review for an equipment item or an owner.

    Attributes:
        id (str): A unique identifier for the review, generated using `generate_short_uuid`.
        equipment (Equipment): The equipment being reviewed (optional).
        owner (User): The owner being reviewed (optional).
        user (User): The user who wrote the review.
        rating (int): The rating given in the review (1 to 5).
        review_text (str): The text content of the review (optional).
        date_created (datetime): The date and time when the review was created.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    equipment = models.ForeignKey(
        'Equipment',
        related_name='equipment_reviews',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='owner_reviews',
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_reviews'
    )
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)]  # Ratings from 1 to 5
    )
    review_text = models.TextField(
        blank=True,
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name_plural = "reviews"

    def __str__(self) -> str:
        """
        Returns the string representation of the review.

        Returns:
            str: A formatted string indicating the review's subject and author.
        """
        if self.equipment:
            return f'Review for {self.equipment.name} by {self.user.username}'
        elif self.owner:
            return f'Review for {self.owner.username} by {self.user.username}'
        return f'Review by {self.user.username}'


class Cart(models.Model):
    """
    Represents a shopping cart for a user.

    Attributes:
        id (str): A unique identifier for the cart, generated using `generate_short_uuid`.
        user (User): The user who owns the cart.
        cart_total_price (Decimal): The total price of all items in the cart.
        total_cart_items (int): The total number of items in the cart.
        date_created (datetime): The date and time when the cart was created.
        date_updated (datetime): The date and time when the cart was last updated.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    cart_total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_cart_items = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the cart.

        Returns:
            str: A formatted string indicating the cart's ID.
        """
        return f"Cart {self.id}"

    @property
    def get_cart_total(self) -> Decimal:
        """
        Calculates the total price of all items in the cart.

        Returns:
            Decimal: The total price of the cart. Returns 0 if the cart is not saved.
        """
        if self.pk is None:  # Check if the instance has been saved
            return Decimal('0.00')
        cart_items = self.cart_items.all()
        total = sum(item.get_cart_item_total for item in cart_items)
        return Decimal(total)

    @property
    def get_cart_items(self) -> int:
        """
        Calculates the total number of items in the cart.

        Returns:
            int: The total number of items in the cart. Returns 0 if the cart is not saved.
        """
        if self.pk is None:
            return 0
        cart_items = self.cart_items.all()
        total = sum(item.quantity for item in cart_items)
        return total

    def save(self, *args, **kwargs):
        """
        Overrides the save method to update the cart's total price and item count before saving.
        """
        self.cart_total_price = self.get_cart_total
        self.total_cart_items = self.get_cart_items
        super().save(*args, **kwargs)


class CartItem(models.Model):
    """
    Represents an item in a user's shopping cart.

    Attributes:
        id (str): A unique identifier for the cart item, generated using `generate_short_uuid`.
        cart (Cart): The cart to which this item belongs.
        item (Equipment): The equipment being added to the cart.
        quantity (int): The quantity of the equipment being rented.
        start_date (date): The start date of the rental period.
        end_date (date): The end date of the rental period.
        ordered (bool): Indicates whether the item has been ordered.
        total (Decimal): The total price for this cart item.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    start_date = models.DateField()
    end_date = models.DateField()
    ordered = models.BooleanField(default=False)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    def __str__(self) -> str:
        """
        Returns the string representation of the cart item.

        Returns:
            str: A formatted string indicating the quantity and name of the item.
        """
        return f"{self.quantity} x {self.item.name} in cart"

    @property
    def get_cart_item_total(self):
        """
        Calculate and return the total price for this cart item.
        """
        if not self.item or self.item.hourly_rate is None:
            return Decimal("0.00")  # Ensure a valid return type

        # Ensure start_date and end_date are datetime.date objects
        start_date = self.start_date
        end_date = self.end_date

        # Convert from string if necessary
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Calculate rental duration
        rental_days = (end_date - start_date).days
        rental_days = max(rental_days, 1)  # Ensure at least 1 rental day is charged


        # Compute total
        total_price = self.quantity * self.item.hourly_rate * rental_days

        return Decimal(total_price)  # Ensure currency precision

    def clean(self):
        """
        Validates rental dates and availability of the item in the cart.

        Raises:
            ValidationError: If the start date is in the past, end date is before start date,
                            the item is unavailable, or the quantity exceeds availability.
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
        Saves the cart item, ensuring the total is calculated beforehand.
        Also updates the parent cart's total price and item count.
        """
        self.total = self.get_cart_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)

        # Update the parent cart
        if self.cart:
            self.cart.save()


class Order(models.Model):
    """
    Represents an order in the system.

    Attributes:
        id (str): A unique identifier for the order, generated using `generate_short_uuid`.
        payment_token (str): A token for payment processing (optional).
        cart (Cart): The cart associated with the order (optional).
        user (User): The user who placed the order.
        status (str): The current status of the order.
        shipping_address (Address): The shipping address for the order (optional).
        billing_address (Address): The billing address for the order (optional).
        payment_status (str): The payment status of the order.
        date_created (datetime): The date and time when the order was created.
        date_ordered (datetime): The date and time when the order was placed (optional).
        order_total_price (Decimal): The total price of the order.
        total_order_items (int): The total number of items in the order.
        ordered (bool): Indicates whether the order has been placed.
    """
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

    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('unpaid', 'Unpaid'),
    ]

    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    payment_token = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    cart = models.ForeignKey(
        Cart,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )
    shipping_address = models.ForeignKey(
        Address,
        related_name='shipping_address',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    billing_address = models.ForeignKey(
        Address,
        related_name='billing_address',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_ordered = models.DateTimeField(blank=True, null=True)
    order_total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_order_items = models.IntegerField(default=0)
    ordered = models.BooleanField(default=False)

    def __str__(self) -> str:
        """
        Returns the string representation of the order.

        Returns:
            str: A formatted string indicating the order ID and user.
        """
        return f"Order {self.id} for {self.user.username}"

    def terminate_rental(self) -> None:
        """
        Terminates the rental by setting the order status to 'canceled'.

        Raises:
            ValueError: If the order status is not 'pending' or 'rented'.
        """
        if self.status in ['pending', 'rented']:
            self.status = 'canceled'
            self.save()
        else:
            raise ValueError("Rental cannot be terminated in the current status.")

    def reorder(self) -> 'Order':
        """
        Reorders a completed, returned, or canceled order.

        Returns:
            Order: The newly created order.

        Raises:
            ValueError: If the order status is not 'completed', 'returned', or 'canceled'.
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
    def get_order_total(self) -> Decimal:
        """
        Calculates the total price of the order, including a 6% service fee.

        Returns:
            Decimal: The total price of the order.
        """
        order_items = self.order_items.all()
        total = sum(item.get_order_item_total for item in order_items)
        service_fee = total * Decimal('0.06')
        return total + service_fee

    @property
    def get_order_items(self) -> int:
        """
        Calculates the total number of items in the order.

        Returns:
            int: The total number of items in the order.
        """
        order_items = self.order_items.all()
        return sum(item.quantity for item in order_items)

    def save(self, *args, **kwargs):
        """
        Saves the order, updating the total price and item count.
        """
        self.order_total_price = self.get_order_total
        self.total_order_items = self.get_order_items
        super().save(*args, **kwargs)


class Image(models.Model):
    """
    Represents an image associated with an equipment item or an order.

    Attributes:
        id (str): A unique identifier for the image, generated using `generate_short_uuid`.
        equipment (Equipment): The equipment to which this image belongs.
        order_item (Order): The order item to which this image belongs (optional).
        is_pickup (bool): Indicates if the image is a pickup image.
        is_return (bool): Indicates if the image is a return image.
        image (ImageField): The image file.
    """
    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    equipment = models.ForeignKey(
        Equipment,
        related_name='images',
        on_delete=models.CASCADE
    )
    order_item = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    is_pickup = models.BooleanField(default=False)  # True = Pickup image
    is_return = models.BooleanField(default=False)  # True = Return image
    image = models.ImageField(upload_to='equipment_images/')

    def __str__(self) -> str:
        """
        Returns the string representation of the image.

        Returns:
            str: A formatted string indicating the image's category and associated equipment.
        """
        category = "Pickup" if self.is_pickup else "Return" if self.is_return else "Normal"
        return f"Image for {self.equipment.name} ({category})"

    def clean(self):
        """
        Validates the image categorization and enforces limits on the number of images per category.

        Raises:
            ValidationError: If the image categorization is invalid or exceeds the allowed limits.
        """
        if self.is_pickup and self.is_return:
            raise ValidationError("An image cannot be both a pickup and a return image.")

        # Count existing images by category
        pickup_count = self.equipment.images.filter(is_pickup=True).count()
        return_count = self.equipment.images.filter(is_return=True).count()
        normal_count = self.equipment.images.filter(is_pickup=False, is_return=False).count()

        # Enforce image limits
        if self.is_pickup and pickup_count >= 3:
            raise ValidationError("An equipment item cannot have more than 3 pickup images.")
        if self.is_return and return_count >= 3:
            raise ValidationError("An equipment item cannot have more than 3 return images.")
        if not self.is_pickup and not self.is_return and normal_count >= 4:
            raise ValidationError("An equipment item cannot have more than 4 normal images.")

        super().clean()

    @property
    def image_url(self) -> str:
        """
        Returns the URL of the image file.

        Returns:
            str: The URL of the image.
        """
        return self.image.url

    class Meta:
        unique_together = ('equipment', 'id')
        verbose_name_plural = "images"


class OrderItem(models.Model):
    """
    Represents an item within an order.

    Attributes:
        id (str): A unique identifier for the order item, generated using `generate_short_uuid`.
        ordered (bool): Indicates whether the item has been ordered.
        item (Equipment): The equipment being ordered.
        order (Order): The order to which this item belongs.
        quantity (int): The quantity of the equipment being rented.
        start_date (date): The start date of the rental period.
        end_date (date): The end date of the rental period.
        total (Decimal): The total price for this order item.
        status (str): The current status of the order item.
        identity_document_type (str): The type of identity document provided (e.g., ID, Driver License, Passport).
        identity_document_image (ImageField): The image of the identity document (optional).
        return_item_condition (str): The condition of the item upon return (optional).
        return_item_condition_custom (str): A custom description of the return condition (optional).
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('pickup', 'Pickup Initiated'),
        ('return', "Return Initiated"),
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
        primary_key=True,
        max_length=16,
        default=generate_short_uuid,
        editable=False
    )
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )
    identity_document_type = models.CharField(
        max_length=50,
        choices=IDENTITY_DOCUMENT_CHOICES,
        default='id'
    )
    identity_document_image = models.ImageField(
        upload_to='pickup_identity_documents/',
        blank=True,
        null=True
    )
    return_item_condition = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    return_item_condition_custom = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        """
        Returns the string representation of the order item.

        Returns:
            str: A formatted string indicating the quantity and name of the item.
        """
        return f"{self.quantity} x {self.item.name} in order"

    @property
    def get_order_item_total(self):
        """
        Calculate and return the total price for this order item.
        """
        if not self.start_date or not self.end_date:
            return Decimal("0.00")  # Return 0 if dates are missing

        rental_days = (self.end_date - self.start_date).days
        rental_days = max(rental_days, 1)  # Ensure at least 1 day is charged


        return self.quantity * self.item.hourly_rate * rental_days
    

    def save(self, *args, **kwargs):
        """
        Saves the order item, ensuring the total is calculated beforehand.
        Also updates the parent order's total price and item count.
        """
        self.total = self.get_order_item_total  # Ensures total is calculated before saving
        super().save(*args, **kwargs)

        if self.order:
            self.order.save()