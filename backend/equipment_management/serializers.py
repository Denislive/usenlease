from rest_framework import serializers
from .models import Category, Tag, Equipment, Image, Specification, Review, Cart, CartItem, Order, OrderItem
from user_management.serializers import AddressSerializer
from user_management.models import Address, User
from django.shortcuts import get_object_or_404

import json

# Serializer for Subcategory model
class SubcategorySerializer(serializers.ModelSerializer):
    ad_count = serializers.SerializerMethodField()  # Custom field for counting ads

    class Meta:
        model = Category
        fields = ['id', 'name', 'ad_count', 'image', 'slug']  # Include 'image' field if it exists

    # Method to count the number of related equipment in this subcategory
    def get_ad_count(self, obj):
        return obj.equipments.count()  # Count of equipments in this subcategory


# Serializer for Category model
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)  # Nested subcategory serializer

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'subcategories', 'image']


# Serializer for Tag model
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']  # Only include the 'name' field of the tag


# Serializer for Review model
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['equipment', 'owner', 'user', 'rating', 'review_text', 'date_created']  # Include review-related fields


# Serializer for Specification model
class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['value']  # Only include the value of the specification

        extra_kwargs = {
            'equipment': {'write_only': True},  # Do not expose equipment field in output
            'name': {'write_only': True}  # Do not expose name field in output
        }


# Serializer for Image model
class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()  # Custom field for image URL

    class Meta:
        model = Image
        fields = ('image_url',)  # Only include 'image_url'

    # Method to get the URL of the image
    def get_image_url(self, obj):
        return obj.image.url


# Serializer for Equipment model
class EquipmentSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)  # Include tags, not required
    images = ImageSerializer(many=True, read_only=True)  # Include related images
    address = AddressSerializer()  # Include Address serializer, writable
    hourly_rate = serializers.FloatField()  # Include hourly rate field
    specifications = SpecificationSerializer(many=True, required=False)  # Include specifications
    equipment_reviews = ReviewSerializer(many=True, read_only=True)  # Include reviews, read-only
    rating = serializers.SerializerMethodField()  # Custom field for average rating

    class Meta:
        model = Equipment
        fields = ['owner', 'id', 'category', 'tags', 'name', 'description', 
                  'images', 'hourly_rate', 'address', 'available_quantity', 
                  'is_available', "specifications", 'equipment_reviews', 'rating']
        extra_kwargs = {
            'slug': {'write_only': True},  # Slug is write-only and not exposed
        }

    # Overriding to_representation to filter out reviews with no text
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['equipment_reviews'] = [review for review in data['equipment_reviews'] if review['review_text']]
        return data

    # Method to get the average rating of equipment
    def get_rating(self, obj):
        return obj.get_average_rating()

    # Overriding create method to handle image, tag, and specification processing
    def create(self, validated_data):
        request = self.context.get('request')

        images = request.FILES.getlist('images') if request else []  # Get images from request
        print("Received images:", images)  # Debugging line

        user = validated_data.pop('owner')
        address_data = validated_data.pop('address')
        name = validated_data.get('name')
        description = validated_data.get('description')
        hourly_rate = validated_data.get('hourly_rate')
        is_available = validated_data.get('is_available')
        category = validated_data.get('category')
        available_quantity = validated_data.get('available_quantity')

        # Create Address instance
        address = Address.objects.create(user=user, **address_data)

        # Create Equipment instance with the remaining validated data
        equipment = Equipment.objects.create(
            owner=user, 
            address=address, 
            name=name,
            description=description,
            hourly_rate=hourly_rate,
            is_available=is_available,
            category=category,
            available_quantity=available_quantity
        )

        # Process and create specifications
        specifications_data = request.data.pop('specifications')
        for spec_data in specifications_data:
            spec_data = json.loads(spec_data)  # Load spec data as JSON
            print("Spec data after loading:", spec_data)  # Debugging line
            for spec in spec_data:
                print("Processing spec:", spec)  # Debugging line
                
                # Create and associate specification with equipment
                Specification.objects.create(
                    equipment=equipment,
                    name=spec['key'],
                    value=spec['value']
                )
                print("Specification created:", spec)  # Debugging line

        # Handle tags if provided
        tags_data = validated_data.pop('tags', [])
        print('Tags data:', tags_data)  # Debugging line

        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)  # Create or get tag
            equipment.tags.add(tag)  # Add tag to equipment

        # Handle images if provided
        for image in images:
            Image.objects.create(equipment=equipment, image=image)  # Create image for equipment
            print(f"Image created: {image}")  # Debugging line

        return equipment


# Serializer for Cart model
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'cart_items']  # Cart fields


# Serializer for CartItem model
class CartItemSerializer(serializers.ModelSerializer):
    item_details = EquipmentSerializer(source='item', read_only=True)  # Include full equipment details
    total = serializers.FloatField(required=False)  # Optional total field

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'item', 'item_details', 'quantity', 'start_date', 'end_date', 'ordered', 'total']


# Serializer for Order model
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'payment_token', 'user', 'status', 'shipping_address', 'billing_address', 
                  'payment_status', 'date_created', 'date_ordered', 'ordered', 'cart', 'order_total_price', 'total_order_items']


# Serializer for OrderItem model
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'ordered', 'item', 'order', 'quantity', 'start_date', 'end_date']  # OrderItem fields
