from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Address, CreditCard, PhysicalAddress, Chat, Message, CompanyInfo, FAQ


# CompanyInfo Admin
@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'updated_at')
    search_fields = ('name', 'email')
    ordering = ('-updated_at',)


# CreditCard Inline for User Admin
class CreditCardInline(admin.TabularInline):
    model = CreditCard
    extra = 1
    fields = (
        'holder_name', 'card_number', 'expiry_date', 'cvc', 'bank_name', 'account_number', 'routing_number',
        'bank_address', 'paypal_email', 'is_default'
    )


# Address Admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_type', 'street_address', 'city', 'zip_code')
    search_fields = ('address_type', 'city', 'state', 'country')
    list_filter = ('address_type', 'city', 'state', 'country')
    ordering = ('-updated_at',)


# PhysicalAddress Admin
@admin.register(PhysicalAddress)
class PhysicalAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'street_address', 'city', 'zip_code')
    search_fields = ('user__username', 'full_name', 'city', 'state', 'country')
    list_filter = ('country', 'full_name', 'city', 'state')
    ordering = ('-updated_at',)


# CreditCard Admin
@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'holder_name', 'card_number', 'expiry_date', 'cvc', 'bank_name', 'account_number', 'routing_number',
        'bank_address', 'paypal_email', 'is_default'
    )
    search_fields = ('user__username', 'holder_name', 'bank_name', 'paypal_email', 'card_number', 'account_number')
    list_filter = ('is_default', 'user')
    ordering = ('-updated_at', 'is_default')


# User Admin
class UserAdmin(BaseUserAdmin):
    inlines = [CreditCardInline]

    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role', 'document_type',
                       'identity_document', 'proof_of_address', 'image', 'is_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone_number'),
        }),
    )
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    def get_email_link(self, obj):
        """Create a link to the user's change page using their email."""
        url = f'/admin/auth/user/{obj.id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.email)

    get_email_link.short_description = 'Email'  # Display name in the admin list view

    def get_first_name_link(self, obj):
        """Create a link to the user's change page using their first name."""
        url = f'/admin/auth/user/{obj.id}/change/'
        return format_html('<a href="{}">{}</a>', url, obj.first_name)

    get_first_name_link.short_description = 'First Name'  # Display name in the admin list view


# Chat Admin
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_filter = ('updated_at', 'created_at', 'item_name')
    search_fields = ('participants__email', 'participants__username', 'item_name')

    ordering = ('-updated_at',)


# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'receiver', 'sent_at', 'seen')
    search_fields = ('sender__username', 'receiver__username', 'content')
    list_filter = ('seen', 'sent_at')
    ordering = ('-sent_at',)


# FAQ Admin
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'updated_at')
    search_fields = ('question', 'answer')
    ordering = ('created_at',)


# Register Models
admin.site.register(User, UserAdmin)