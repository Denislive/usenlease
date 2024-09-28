from rest_framework import serializers
from .models import Equipment

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = (
            'id',
            'owner',
            'category',
            'tags',
            'name',
            'description',
            'hourly_rate',
            'address',
            'is_available',
            'date_created',
            'date_updated',
            'terms',
            'slug',
            'get_absolute_url',
        )
