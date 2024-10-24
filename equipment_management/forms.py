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