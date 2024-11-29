from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address, CreditCard, PhysicalAddress

from django.utils.html import format_html


# Inline for CreditCard, to show related credit card entries within the User admin page
class CreditCardInline(admin.TabularInline):
    model = CreditCard  # The model associated with this inline
    extra = 1  # Number of empty forms to display initially
    fields = ('holder_name', 'card_number', 'expiry_date', 'cvc', 'bank_name', 'account_number', 'routing_number', 'bank_address', 'paypal_email', 'is_default')


# Admin customization for the Address model
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_type', 'street_address', 'city', 'zip_code')  # Fields to display in the list view
    search_fields = ('address_type', 'city', 'state', 'country')  # Fields that can be searched in the admin panel
    list_filter = ('address_type', 'city', 'state', 'country')  # Filters to display in the sidebar
    ordering = ('-updated_at',)  # Default ordering (latest updated first)


# Admin customization for the PhysicalAddress model
class PhysicalAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'street_address', 'city', 'zip_code')  # Fields to display in the list view
    search_fields = ('user__username', 'full_name', 'city', 'state', 'country')  # Searchable fields
    list_filter = ('country', 'full_name', 'city', 'state')  # Filter options
    ordering = ('-updated_at',)  # Default ordering


# Admin customization for the CreditCard model
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'holder_name', 'card_number', 'expiry_date', 'cvc', 'bank_name', 'account_number', 'routing_number', 'bank_address', 'paypal_email', 'is_default')  # Displayed fields
    search_fields = ('user__username', 'holder_name', 'bank_name', 'paypal_email', 'card_number', 'account_number')  # Searchable fields
    list_filter = ('is_default', 'user')  # Filters for default card status and user
    ordering = ('-updated_at', 'is_default')  # Default ordering


# Admin customization for the User model (inherits from BaseUserAdmin)
class UserAdmin(BaseUserAdmin):
    inlines = [CreditCardInline]  # Include the CreditCardInline in the User admin page

    model = User  # The model this admin is associated with
    list_display = ('email', 'first_name', 'last_name', 'role', 'phone_number')  # Fields to display in the list view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),  # Fields for username and password
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role', 'document_type', 'identity_document', 'proof_of_address')}),  # Personal info section
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),  # Permissions section
        ('Important dates', {'fields': ('last_login', 'date_joined')}),  # Dates section (when the user last logged in, when they joined)
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # CSS classes to apply for styling
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone_number'),  # Fields for user creation
        }),
    )

    def get_email_link(self, obj):
        # Create a clickable link to the user's change page in the admin panel (for email field)
        url = f'/admin/auth/user/{obj.id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.email)
    
    get_email_link.short_description = 'Email'  # Set the label for this field in the admin list view

    def get_first_name_link(self, obj):
        # Create a clickable link to the user's change page in the admin panel (for first name field)
        url = f'/admin/auth/user/{obj.id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.first_name)
    
    get_first_name_link.short_description = 'First Name'  # Set the label for this field in the admin list view


    search_fields = ('username', 'email', 'phone_number')  # Fields that can be searched
    ordering = ('-date_joined',)  # Default ordering by the most recent user

# Register the models with the admin site
admin.site.register(User, UserAdmin)  # Register the User model with custom admin
admin.site.register(Address, AddressAdmin)  # Register the Address model
admin.site.register(PhysicalAddress, PhysicalAddressAdmin)  # Register the PhysicalAddress model
admin.site.register(CreditCard, CreditCardAdmin)  # Register the CreditCard model
