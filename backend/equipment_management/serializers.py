from rest_framework import serializers
from .models import Category, Tag, Equipment, Image, Specification, Review, Cart, CartItem, Order, OrderItem
from user_management.serializers import AddressSerializer
from user_management.models import Address, User
from django.shortcuts import get_object_or_404


import json

class SubcategorySerializer(serializers.ModelSerializer):
    ad_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'ad_count', 'image', 'slug']  # Include 'image' field if it exists

    def get_ad_count(self, obj):
        # Assuming you have a related_name 'equipments' in your Category model
        return obj.equipments.count()  # Count of equipments in this subcategory

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    ad_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'subcategories', 'image', 'ad_count']

    def get_ad_count(self, obj):
        # Count equipment directly in the category
        direct_count = obj.equipments.count()

        # If the category has subcategories, sum their ad counts
        if obj.subcategories.exists():
            subcategory_count = sum(sub.equipments.count() for sub in obj.subcategories.all())
            return direct_count + subcategory_count
        
        # If no subcategories, return only the direct count
        return direct_count

      


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['equipment', 'owner', 'user', 'rating', 'review_text', 'date_created']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['value']

        extra_kwargs = {
            'equipment': {'write_only':True},
            'name': {'write_only':True}
        }


# Serializer for the Image model
class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ('image_url',)

    # Method to get the URL of the image
    def get_image_url(self, obj):
        return obj.image.url

class EquipmentSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    images = ImageSerializer(many=True, read_only=True)  # Include related images
    address = AddressSerializer()  # Allow writable Address field
    hourly_rate = serializers.FloatField()
    specifications = SpecificationSerializer(many=True,required=False)
    equipment_reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = ['owner', 'id', 'category', 'tags', 'name', 'description', 
                  'images', 'hourly_rate', 'address', 'available_quantity', 
                  'is_available', "specifications", 'terms', 'equipment_reviews', 'rating', 'is_trending', 'is_featured']
        extra_kwargs = {
            'slug': {'write_only': True},   # Slug is write-only and not exposed
        }
    
    def to_representation(self, instance):
        # Filter out reviews with no review_text before returning the data
        data = super().to_representation(instance)
        data['equipment_reviews'] = [review for review in data['equipment_reviews'] if review['review_text']]
        return data

    def get_rating(self, obj):
        return obj.get_average_rating()

    def create(self, validated_data):
        # Access the request from the context
        request = self.context.get('request')

        # Retrieve the uploaded images from request.FILES
        images = request.FILES.getlist('images') if request else []
        print("Received images:", images)

        user = validated_data.pop('owner')
        address_data = validated_data.pop('address')
        name = validated_data.get('name')
        description = validated_data.get('description')
        hourly_rate = validated_data.get('hourly_rate')
        is_available = validated_data.get('is_available')
        category = validated_data.get('category')
        available_quantity = validated_data.get('available_quantity')
        terms =validated_data.get('terms')

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
            terms=terms,
            available_quantity=available_quantity
        )

        return equipment







class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'cart_items']

class CartItemSerializer(serializers.ModelSerializer):
    item_details = EquipmentSerializer(source='item', read_only=True)  # Full details on read
    total = serializers.FloatField(required=False)
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'item', 'item_details', 'quantity', 'start_date', 'end_date', 'ordered', 'total']

class OrderSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = Order
        fields = ['id', 'payment_token', 'user', 'status', 'shipping_address', 'billing_address', 
                  'payment_status', 'date_created', 'date_ordered', 'ordered', 'cart', 'order_total_price', 'total_order_items']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'ordered', 'item', 'order', 'quantity', 'start_date', 'end_date']