from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    User,
    Address,
    CreditCard,
    PhysicalAddress,
    OTP,
    Message,
    Chat,
    Contact,
    CompanyInfo,
    FAQ
)
from .utils import generate_signed_url


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contact model.

    Attributes:
        name (str): The name of the contact.
        email (str): The email of the contact.
        message (str): The message from the contact.
    """
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']


class OTPSerializer(serializers.ModelSerializer):
    """
    Serializer for the OTP model.

    Attributes:
        id (int): The unique identifier for the OTP.
        user (User): The user associated with the OTP.
        code (str): The OTP code.
        created_at (datetime): The date and time when the OTP was created.
        expires_at (datetime): The date and time when the OTP expires.
    """
    class Meta:
        model = OTP
        fields = ['id', 'user', 'code', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address model.

    Attributes:
        street_address (str): The primary street address.
        street_address2 (str): Additional address information (optional).
        city (str): The city of the address.
        state (str): The state or region of the address.
        zip_code (str): The postal code of the address.
        country (str): The country of the address.
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
        write_only_fields = ['id', 'address_type', 'is_default']  # Make these fields write-only


class CompanyInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the CompanyInfo model.

    Attributes:
        address (dict): The address of the company.
    """
    address = AddressSerializer(read_only=True)

    class Meta:
        model = CompanyInfo
        fields = '__all__'

    def update(self, instance, validated_data):
        """
        Updates the CompanyInfo instance, including nested address data if provided.

        Args:
            instance (CompanyInfo): The CompanyInfo instance to update.
            validated_data (dict): The validated data for the update.

        Returns:
            CompanyInfo: The updated CompanyInfo instance.
        """
        address_data = validated_data.pop('address', None)
        if address_data:
            address_serializer = AddressSerializer(instance.address, data=address_data)
            if address_serializer.is_valid():
                address_serializer.save()

        return super().update(instance, validated_data)


class PhysicalAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the PhysicalAddress model.

    Attributes:
        id (int): The unique identifier for the physical address.
        full_name (str): The full name associated with the address.
        company_name (str): The company name associated with the address (optional).
        street_address (str): The primary street address.
        street_address2 (str): Additional address information (optional).
        city (str): The city of the address.
        state (str): The state or region of the address.
        zip_code (str): The postal code of the address.
        country (str): The country of the address.
        is_default (bool): Indicates whether this is the default address.
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

    Attributes:
        user_address (dict): The physical address associated with the user.
    """
    user_address = PhysicalAddressSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
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
            'password': {'write_only': True},
            'document_type': {'write_only': True},
            'identity_document': {'write_only': True},
            'proof_of_address': {'write_only': True},
        }


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    Attributes:
        sender (User): The user who sent the message.
        receiver (User): The user who received the message.
        chat (Chat): The chat to which the message belongs (optional).
        signed_image_url (str): A signed URL for the image (if it exists).
    """
    sender = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False)
    receiver = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    chat = serializers.PrimaryKeyRelatedField(queryset=Chat.objects.all(), required=False)
    signed_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'content', 'sent_at', 'is_deleted', 'seen', 'chat', 'image_url', 'signed_image_url'
        ]

    def get_signed_image_url(self, obj) -> str:
        """
        Generates a signed URL for the image if it exists.

        Args:
            obj (Message): The message instance.

        Returns:
            str: The signed URL of the image, or None if no image exists.
        """
        if obj.image_url:
            return generate_signed_url("usenlease-media", obj.image_url)
        return None


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for the Chat model.

    Attributes:
        participants (list): A list of users participating in the chat.
        messages (list): A list of messages in the chat.
    """
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'messages', 'created_at', 'updated_at']


class CreditCardSerializer(serializers.ModelSerializer):
    """
    Serializer for the CreditCard model.

    Attributes:
        id (int): The unique identifier for the credit card.
        holder_name (str): The name of the cardholder.
        card_number (str): The credit card number.
        expiry_date (str): The expiration date of the card.
        cvc (str): The card verification code.
        bank_name (str): The name of the bank associated with the card.
        account_number (str): The bank account number.
        routing_number (str): The bank routing number.
        bank_address (str): The address of the bank.
        paypal_email (str): The PayPal email associated with the card.
        is_default (bool): Indicates whether this is the default credit card.
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


class FAQSerializer(serializers.ModelSerializer):
    """
    Serializer for the FAQ model.

    Attributes:
        id (int): The unique identifier for the FAQ.
        question (str): The question being asked.
        answer (str): The answer to the question.
        created_at (datetime): The date and time when the FAQ was created.
        updated_at (datetime): The date and time when the FAQ was last updated.
    """
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'created_at', 'updated_at']