# Standard Library Imports
import json
from collections import defaultdict

# Django Imports
from django.shortcuts import get_object_or_404
from django.db.models import Sum

# Django REST Framework Imports
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

# Local Imports
from .models import Category, Tag, Equipment, Image, Specification, Review, Cart, CartItem, Order, OrderItem
from user_management.serializers import AddressSerializer
from user_management.models import Address, User


class SubcategorySerializer(serializers.ModelSerializer):
    """
    Serializer for subcategories, including the count of associated equipment.

    Attributes:
        ad_count (int): The number of equipment items associated with the subcategory.
    """
    ad_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'ad_count', 'image', 'slug']

    def get_ad_count(self, obj) -> int:
        """
        Returns the count of equipment items associated with the subcategory.

        Args:
            obj (Category): The subcategory instance.

        Returns:
            int: The count of equipment items.
        """
        return obj.equipments.count()


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories, including subcategories and the count of associated equipment.

    Attributes:
        subcategories (list): A list of subcategories under this category.
        ad_count (int): The total count of equipment items in this category and its subcategories.
    """
    subcategories = SubcategorySerializer(many=True, read_only=True)
    ad_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'subcategories', 'image', 'ad_count']

    def get_ad_count(self, obj) -> int:
        """
        Returns the total count of equipment items in this category and its subcategories.

        Args:
            obj (Category): The category instance.

        Returns:
            int: The total count of equipment items.
        """
        direct_count = obj.equipments.count()  # Count equipment directly in the category

        # Sum equipment counts from subcategories if they exist
        if obj.subcategories.exists():
            subcategory_count = sum(sub.equipments.count() for sub in obj.subcategories.all())
            return direct_count + subcategory_count

        return direct_count  # Return only the direct count if no subcategories exist


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model.

    Attributes:
        name (str): The name of the tag.
    """
    class Meta:
        model = Tag
        fields = ['name']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.

    Attributes:
        equipment (Equipment): The equipment being reviewed.
        owner (User): The owner of the equipment being reviewed.
        user (User): The user who wrote the review.
        rating (int): The rating given in the review.
        review_text (str): The text content of the review.
        date_created (datetime): The date and time when the review was created.
    """
    class Meta:
        model = Review
        fields = ['equipment', 'owner', 'user', 'rating', 'review_text', 'date_created']


class SpecificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Specification model.

    Attributes:
        value (str): The value of the specification.
    """
    class Meta:
        model = Specification
        fields = ['name', 'value']
        extra_kwargs = {
            'equipment': {'write_only': True},  # Hide equipment field in responses
        }


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Image model.

    Attributes:
        image_url (str): The URL of the image file.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['image_url']

    def get_image_url(self, obj) -> str:
        """
        Returns the URL of the image file.

        Args:
            obj (Image): The image instance.

        Returns:
            str: The URL of the image.
        """
        return obj.image.url



class EquipmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Equipment model.

    Attributes:
        tags (list): A list of tags associated with the equipment.
        images (list): A list of images associated with the equipment.
        address (dict): The address of the equipment.
        hourly_rate (float): The hourly rental rate of the equipment.
        specifications (list): A list of specifications for the equipment.
        equipment_reviews (list): A list of reviews for the equipment.
        rating (float): The average rating of the equipment.
        booked_dates_data (list): A list of booked dates and quantities for the equipment.
        total_booked (int): The total quantity of the equipment booked.
    """
    tags = TagSerializer(many=True, required=False)
    images = ImageSerializer(many=True, read_only=True)
    address = AddressSerializer()
    hourly_rate = serializers.FloatField()
    specifications = SpecificationSerializer(many=True, required=False)
    equipment_reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    booked_dates_data = serializers.SerializerMethodField()
    total_booked = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = [
            'owner', 'id', 'category', 'tags', 'name', 'description', 'images', 'hourly_rate', 'address',
            'available_quantity', 'is_available', 'specifications', 'equipment_reviews', 'rating', 'terms',
            'is_trending', 'is_featured', 'booked_dates_data', 'total_booked'
        ]
        extra_kwargs = {
            'slug': {'write_only': True},  # Slug is write-only and not exposed
        }

    def to_representation(self, instance):
        """
        Filters out reviews with no review_text before returning the data.

        Args:
            instance (Equipment): The equipment instance.

        Returns:
            dict: The serialized representation of the equipment.
        """
        data = super().to_representation(instance)
        data['equipment_reviews'] = [review for review in data['equipment_reviews'] if review['review_text']]
        return data

    def get_rating(self, obj) -> float:
        """
        Returns the average rating of the equipment.

        Args:
            obj (Equipment): The equipment instance.

        Returns:
            float: The average rating of the equipment.
        """
        return obj.get_average_rating()

    def get_total_booked(self, obj) -> int:
        """
        Returns the total quantity of the equipment booked.

        Args:
            obj (Equipment): The equipment instance.

        Returns:
            int: The total quantity booked.
        """
        total_booked = OrderItem.objects.filter(item=obj).aggregate(total=Sum('quantity'))['total'] or 0
        return total_booked

    def get_booked_dates_data(self, obj) -> list:
        """
        Returns a list of booked dates and quantities for the equipment.

        Args:
            obj (Equipment): The equipment instance.

        Returns:
            list: A list of dictionaries containing booked dates and quantities.
        """
        order_items = OrderItem.objects.filter(item=obj)
        grouped_bookings = defaultdict(int)

        for order_item in order_items:
            date_range_key = (order_item.start_date, order_item.end_date)
            grouped_bookings[date_range_key] += order_item.quantity  # Sum up the quantities

        booked_dates_data = [
            {'quantity': quantity, 'start_date': start, 'end_date': end}
            for (start, end), quantity in grouped_bookings.items()
        ]

        return booked_dates_data

    def create(self, validated_data):
        """
        Creates an Equipment instance with the provided validated data.

        Args:
            validated_data (dict): The validated data for creating the equipment.

        Returns:
            Equipment: The created equipment instance.

        Raises:
            PermissionDenied: If the user is not authenticated or is not a lessor.
        """
        request = self.context.get('request')
        user = request.user

        if user.is_anonymous:
            raise PermissionDenied("You must be authenticated")

        if user.role == 'lessee':
            raise PermissionDenied("Please change role to Lessor to list an Item!")

        images = request.FILES.getlist('images') if request else []
        validated_data.pop('owner', None)
        address_data = validated_data.pop('address')

        address = Address.objects.create(user=user, **address_data)
        equipment = Equipment.objects.create(owner=user, address=address, **validated_data)

        return equipment


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.

    Attributes:
        id (int): The unique identifier for the cart.
        cart_items (list): A list of items in the cart.
    """
    class Meta:
        model = Cart
        fields = ['id', 'cart_items']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartItem model.

    Attributes:
        item_details (dict): Detailed information about the equipment item.
        total (float): The total price for the cart item.
    """
    item_details = EquipmentSerializer(source='item', read_only=True)  # Full details on read
    total = serializers.FloatField(required=False)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'item', 'item_details', 'quantity', 'start_date', 'end_date', 'ordered', 'total']

    def validate(self, data):
        """
        Validates the availability of the equipment for the selected dates and quantity.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the item is not available or the quantity exceeds availability.
        """
        item = data.get('item')
        quantity = data.get('quantity')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Retrieve the equipment and validate its availability
        equipment = Equipment.objects.get(id=item.id)

        # Check if the item is available during the provided dates
        if not equipment.is_available_for_dates(start_date, end_date):
            raise serializers.ValidationError(f"The item '{equipment.name}' is not available for the selected dates.")

        # Check if the requested quantity exceeds the available quantity
        if quantity > equipment.get_available_quantity(start_date, end_date):
            raise serializers.ValidationError(
                f"Only {equipment.get_available_quantity(start_date, end_date)} items are available for the selected dates."
            )

        return data


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.

    Attributes:
        item (dict): Detailed information about the equipment item.
        booked_dates (dict): The booked dates and quantity for the order item.
        total_booked (int): The total quantity of the related equipment booked.
    """
    item = EquipmentSerializer()
    booked_dates = serializers.SerializerMethodField()
    total_booked = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'ordered', 'item', 'order', 'quantity', 'start_date', 'end_date', 'booked_dates', 'total_booked',
            'status', 'identity_document_type', 'identity_document_image', 'return_item_condition', 'return_item_condition_custom'
        ]

    def get_booked_dates(self, obj) -> dict:
        """
        Returns the booked dates and quantity for the order item.

        Args:
            obj (OrderItem): The order item instance.

        Returns:
            dict: A dictionary containing the start date, end date, and quantity.
        """
        return {
            "start_date": obj.start_date,
            "end_date": obj.end_date,
            "quantity": obj.quantity
        }

    def get_total_booked(self, obj) -> int:
        """
        Returns the total quantity of the related equipment booked.

        Args:
            obj (OrderItem): The order item instance.

        Returns:
            int: The total quantity booked.
        """
        total = OrderItem.objects.filter(item=obj.item).aggregate(total=Sum('quantity'))['total']
        return total or 0


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    Attributes:
        order_items (list): A list of order items associated with the order.
    """
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'payment_token', 'user', 'status', 'shipping_address', 'billing_address', 'payment_status',
            'date_created', 'date_ordered', 'ordered', 'cart', 'order_total_price', 'total_order_items', 'order_items'
        ]