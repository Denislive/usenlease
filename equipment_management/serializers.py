from rest_framework import serializers
from .models import Category, Tag, Equipment, Image, Specification, Review, Cart, CartItem, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'parent', 'image']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['equipment', 'owner', 'user', 'rating', 'review_text', 'date_created']


class EquipmentSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Equipment
        fields = ['category', 'tags', 'name', 'description', 
                  'hourly_rate', 'address', 'available_quantity', 
                  'is_available']
        extra_kwargs = {
            'owner': {'write_only': True},  # Owner is set via the request, not exposed
            'slug': {'write_only': True},   # Slug is write-only and not exposed
            'terms': {'write_only': True},  # Terms are write-only, not exposed
        
        }

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['equipment', 'image']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['equipment', 'name', 'value']



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'cart_total_price', 'total_cart_items', 'date_created', 'date_updated']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'item', 'quantity', 'start_date', 'end_date', 'ordered', 'total']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'payment_token', 'user', 'status', 'shipping_address', 'billing_address', 
                  'payment_status', 'date_created', 'date_ordered', 'ordered']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'ordered', 'item', 'order', 'quantity', 'start_date', 'end_date']