# rentals/serializers.py
from rest_framework import serializers
from .models import User, Address, CreditCard,  PhysicalAddress



from rest_framework import serializers
from .models import User


from .models import OTP

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['id', 'user', 'code', 'created_at', 'expires_at']
        read_only_fields = ['created_at', 'expires_at']



class AddressSerializer(serializers.ModelSerializer):
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
        write_only_fields = ['id', 'address_type', 'is_default']  # Make these fields read-only


class PhysicalAddressSerializer(serializers.ModelSerializer):
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
    user_address = PhysicalAddressSerializer(read_only=True)
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
            'id': {'write_only': True},  # Make id write-only
            'password': {'write_only': True},  # Ensure password is write-only
            'document_type': {'write_only': True},
            'identity_document': {'write_only': True},
            'proof_of_address': {'write_only': True},
        }

    



class CreditCardSerializer(serializers.ModelSerializer):
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