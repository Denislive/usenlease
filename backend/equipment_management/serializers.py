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
                  'is_available', "specifications", 'terms', 'equipment_reviews', 'rating']
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


        # Extract the specifications data
        specifications_data = request.data.pop('specifications')

        # Create the specification objects and associate them with the equipment
        for spec_data in specifications_data:
            spec_data = json.loads(spec_data)  # Assuming you need to load the spec data as JSON
            print("Spec data after loading:", spec_data)  # Debugging line
            
            for spec in spec_data:
                print("Processing spec:", spec)  # Debugging line
                
                # Create the specification and associate it with the equipment instance
                Specification.objects.create(
                    equipment=equipment,  # Associate the specification with the equipment
                    name=spec['key'],     # Assuming 'key' is the name of the specification
                    value=spec['value']   # Assuming 'value' is the value of the specification
                )

                print("Specification created:", spec)  # Debugging line


        # # Extract the specifications data
        # specifications_data = request.data.get('specifications', [])
        # print("Specifications data:", specifications_data)

        # # Create the specification objects and associate them with the equipment
        # for spec_data in specifications_data:
        #     # Check if spec_data is a string and needs to be loaded from JSON
        #     if isinstance(spec_data, str):
        #         try:
        #             spec_data = json.loads(spec_data)
        #             print("Parsed specification:", spec_data)
        #         except json.JSONDecodeError as e:
        #             print(f"Error decoding specification data: {e}")
        #             continue

        #     # Loop through the specification data (expecting a list of dicts)
        #     for spec in spec_data:
        #         print("Processing spec:", spec)
        #         name = spec.get('key')
        #         value = spec.get('value')

        #         # Check if 'key' and 'value' exist in the spec
        #         if not name or not value:
        #             print(f"Invalid specification data: {spec}. Missing 'key' or 'value'.")
        #             continue  # Skip invalid specification data

        #         # Ensure the equipment field is correctly assigned
        #         specification_data = {
        #             'equipment': equipment,
        #             'name': name,  # Renamed from 'key' to 'name'
        #             'value': value
        #         }

        #         # Now use the Specification serializer to validate and create the specification instance
        #         specification_serializer = SpecificationSerializer(data=specification_data)
        #         if specification_serializer.is_valid():
        #             specification_serializer.save()  # Create the specification instance
        #             print(f"Specification created: {specification_serializer.data}")
        #         else:
        #             print(f"Specification errors: {specification_serializer.errors}")
        #             continue

        # Handle tags if they exist
        tags_data = validated_data.pop('tags', [])
        print('Tags data:', tags_data)  # Debugging line to see tags_data

        for tag_name in tags_data:
            # Assuming tag_name is a string; if it's a dict, adjust accordingly
            tag, created = Tag.objects.get_or_create(name=tag_name)  # Create or get the tag
            equipment.tags.add(tag)  # Add tag to equipment's many-to-many field

        # Handle images if they exist
        for image in images:
            # Create an Image instance associated with the equipment
            Image.objects.create(equipment=equipment, image=image)
            print(f"Image created: {image}")

        return equipment







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