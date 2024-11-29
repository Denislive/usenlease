# rentals/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import User, Address, CreditCard, PhysicalAddress, OTP, Message, Chat


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    """
    sender = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False)
    receiver = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), required=False)  # Allow chat to be optional

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'sent_at', 'is_deleted', 'seen', 'chat']


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for the Chat model.
    """
    participants = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), many=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'messages', 'created_at', 'updated_at']


class OTPSerializer(serializers.ModelSerializer):
    """
    Serializer for the OTP model.
    """
    class Meta:
        model = OTP
        fields = ['id', 'user', 'code', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']  # These fields are read-only.


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address model.
    """
    class Meta:
        model = Address
        fields = [
            'street_address',
            'street_address2',
            'city',
            'state',
            'zip_code',
            'country',
        ]
        write_only_fields = ['id', 'address_type', 'is_default']  # These fields are write-only.


class PhysicalAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the PhysicalAddress model.
    """
    class Meta:
        model = PhysicalAddress
        fields = [
            'id',
            'full_name',
            'company_name',
            'street_address',
            'street_address2',
            'city',
            'state',
            'zip_code',
            'country',
            'is_default'
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    user_address = PhysicalAddressSerializer(read_only=True)  # Nested serializer for user's address.

    class Meta:
        model = User
        fields = [
            'image',
            'first_name',
            'last_name',
            'company_name',
            'username',
            'role',
            'phone_number',
            'email',
            'user_address',
            'document_type',
            'identity_document',
            'proof_of_address',
            'password'
        ]
        extra_kwargs = {
            'id': {'write_only': True},  # Make id write-only.
            'password': {'write_only': True},  # Ensure password is write-only.
            'document_type': {'write_only': True},
            'identity_document': {'write_only': True},
            'proof_of_address': {'write_only': True},
        }


class CreditCardSerializer(serializers.ModelSerializer):
    """
    Serializer for the CreditCard model.
    """
    class Meta:
        model = CreditCard
        fields = [
            'id',
            'holder_name',
            'card_number',
            'expiry_date',
            'cvc',
            'bank_name',
            'account_number',
            'routing_number',
            'bank_address',
            'paypal_email',
            'is_default'
        ]
