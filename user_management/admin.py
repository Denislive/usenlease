from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address, CreditCard, PhysicalAddress

from django.utils.html import format_html


class CreditCardInline(admin.TabularInline):
    model = CreditCard
    extra = 1
    fields = ('holder_name', 'card_number', 'expiry_date', 'cvc', 'bank_name', 'account_number', 'routing_number', 'bank_address', 'paypal_email', 'is_default')
    readonly_fields = ('is_default',)  # Make is_default field read-only


class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_type', 'street_address', 'city', 'zip_code')
    search_fields = ('address_type', 'city', 'state', 'country')
    list_filter = ('address_type', 'country')
    ordering = ('-updated_at',)



class PhysicalAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'street_address', 'city', 'zip_code')
    search_fields = ('user__username', 'full_name', 'city', 'state', 'country')
    list_filter = ('country',)
    ordering = ('-updated_at',)


class CreditCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'holder_name', 'card_number', 'expiry_date', 'cvc', 'bank_name', 'account_number', 'routing_number', 'bank_address', 'paypal_email', 'is_default')
    search_fields = ('user__username', 'holder_name', 'bank_name', 'paypal_email')
    list_filter = ('is_default', 'user')
    ordering = ('-updated_at', 'is_default')

class UserAdmin(BaseUserAdmin):
    inlines = [CreditCardInline]

    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'phone_number')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role', 'document_type', 'identity_document', 'proof_of_address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone_number'),
        }),
        
    )

    def get_email_link(self, obj):
        # Create a link to the user's change page
        url = f'/admin/auth/user/{obj.id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.email)
    
    get_email_link.short_description = 'Email'  # Display name in the admin list view

    def get_first_name_link(self, obj):
        # Create a link to the user's change page
        url = f'/admin/auth/user/{obj.id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.first_name)
    
    get_first_name_link.short_description = 'First Name'  # Display name in the admin list view


    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)



admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PhysicalAddress, PhysicalAddressAdmin)
admin.site.register(CreditCard, CreditCardAdmin)

