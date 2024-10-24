# serializers.py
from rest_framework import serializers
from .models import Category, Tag, Equipment, Image, Specification, Review, Cart, CartItem, Order, OrderItem
from user_management.serializers import AddressSerializer
from user_management.models import Address

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
        fields = ['id', 'name', 'slug', 'description', 'image', 'subcategories']



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


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
    images = ImageSerializer(many=True, read_only=True)  # Include related images
    address = AddressSerializer()  # Allow writable Address field
    tags = TagSerializer(many=True, write_only=True)  # Allow writable Tags

    class Meta:
        model = Equipment
        fields = ['id', 'owner', 'name', 'description', 'hourly_rate', 'is_available', 'images', 'terms', 'category', 'slug', 'address', 'tags']

    def create(self, validated_data):
        # Pop address and tags data from validated_data
        address_data = validated_data.pop('address')
        tags_data = validated_data.pop('tags', [])  # Get tags data, default to empty list
        owner = validated_data.get('owner')  # Get the owner (user)

        # Create Address instance
        address = Address.objects.create(user=owner, **address_data)
        
        # Now create the Equipment instance, passing the address
        equipment = Equipment.objects.create(address=address, **validated_data)

        # Handle the tags
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(**tag_data)  # Create or get the tag
            equipment.tags.add(tag)  # Associate the tag with the Equipment

        return equipment







class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'session_key', 'date_created', 'cart_items']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'