from django import forms
from .models import Equipment, Order, OrderItem, Category, Tag, Image, Review

from django.contrib.auth import get_user_model
from user_management.models import Address, PhysicalAddress

User = get_user_model()


class EquipmentReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(),
        }


class EquipmentForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Type tags separated by commas'}),
        required=False
    )
    hourly_rate = forms.DecimalField(max_digits=10, decimal_places=2)
    street_address = forms.CharField(max_length=255)
    street_address2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255)
    state = forms.CharField(max_length=255)
    zip_code = forms.CharField(max_length=10)
    is_available = forms.BooleanField(required=False)
    terms = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure all address fields are provided
        if not cleaned_data.get('street_address') or \
           not cleaned_data.get('city') or \
           not cleaned_data.get('state') or \
           not cleaned_data.get('zip_code'):
            raise forms.ValidationError('Please provide complete address details.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(parent=None)  # Only show top-level categories

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date cannot be before start date.')

        return cleaned_data



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']