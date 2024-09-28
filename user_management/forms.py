from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Address, PhysicalAddress, CreditCard
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email Address', max_length=254)

    class Meta:
        model = User
        fields = ['username', 'password']

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'role', 'document_type', 'identity_document', 'proof_of_address', 'password1', 'password2']


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['phone_number', 'document_type', 'identity_document', 'proof_of_address']



class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields =  ['street_address', 'street_address2', 'city', 'state', 'zip_code', 'country', 'address_type', 'is_default']

    


class CheckoutForm(forms.Form):

    SHIPPING_METHODS = [
        ('SP', 'Self Pickup'),
        ('OW', 'One-Way Delivery'),
        ('TW', 'Two-Way Delivery'),
    ]

    PAYMENT_METHODS = [
        ('S', 'Stripe'),
        ('P', 'Paypal'),
    ]

    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = forms.CharField(required=False)
    shipping_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)

    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = forms.CharField(required=False)
    billing_zip = forms.CharField(required=False)

    

    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    shipping_method = forms.ChoiceField(choices=SHIPPING_METHODS)

    payment_method = forms.ChoiceField(choices=PAYMENT_METHODS)

    

    


class PhysicalAddressForm(forms.ModelForm):

    same_as_billing = forms.BooleanField(required=False, label="Same as Billing Address", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    same_as_shipping = forms.BooleanField(required=False, label="Same as Shipping Address", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = PhysicalAddress
        fields = ['full_name', 'company_name', 'street_address', 'street_address2', 'city', 'state', 'zip_code', 'country']

    
    


class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = ['holder_name', 'card_number', 'expiry_date', 'cvc', 'bank_name', 'account_number', 'routing_number', 'bank_address', 'paypal_email', 'is_default']

