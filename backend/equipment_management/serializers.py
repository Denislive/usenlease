from rest_framework import serializers
from .models import Category, Tag, Equipment, Image, Specification, Review, Cart, CartItem, Order, OrderItem
from user_management.serializers import AddressSerializer
from user_management.models import Address, User
from django.shortcuts import get_object_or_404

class SubcategorySerializer(serializers.ModelSerializer):
    ad_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'ad_count', 'image', 'slug']  # Include 'image' field if it exists

    def get_ad_count(self, obj):
        # Assuming you have a related_name 'equipments' in your Category model
        return obj.equipments.count()  # Count of equipments in this subcategory


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)  # Nested subcategory serializer

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'subcategories', 'image']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['equipment', 'owner', 'user', 'rating', 'review_text', 'date_created']


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

    class Meta:
        model = Equipment
        fields = ['owner', 'id', 'category', 'tags', 'name', 'description', 
                  'images', 'hourly_rate', 'address', 'available_quantity', 
                  'is_available']
        extra_kwargs = {
            'slug': {'write_only': True},   # Slug is write-only and not exposed
            'terms': {'write_only': True},  # Terms are write-only, not exposed
        }

    def create(self, validated_data):
        # Access the request from the context
        request = self.context.get('request')

        # Retrieve the uploaded images from request.FILES
        images = request.FILES.getlist('images') if request else []
          
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

        # Handle tags if they exist
        tags_data = validated_data.pop('tags', [])
        print('tags data', tags_data)  # Debugging line to see tags_data

        for tag_name in tags_data:
            # Assuming tag_name is a string; if it's a dict, adjust accordingly
            tag, created = Tag.objects.get_or_create(name=tag_name)  # Create or get the tag
            equipment.tags.add(tag)  # Add tag to equipment's many-to-many field

        print()
        print("images", images)
        # Handle images if they exist
        for image in images:
            # Create an Image instance associated with the equipment
            # Assuming your Image model has a foreign key to Equipment
            Image.objects.create(equipment=equipment, image=image)
            print()
            print('image created')

        return equipment



class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['equipment', 'name', 'value']



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['cart_items']

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
                  'payment_status', 'date_created', 'date_ordered', 'ordered']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'ordered', 'item', 'order', 'quantity', 'start_date', 'end_date']