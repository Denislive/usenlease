from django.contrib import admin
from .models import Category, Tag, Equipment, Image, Cart, CartItem, Order, OrderItem, Specification, Review


# Inline model for Images in Equipment
class ImageInline(admin.TabularInline):
    model = Image
    extra = 1  # Number of extra blank images to display in the admin


# Equipment Admin
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'hourly_rate', 'is_available', 'date_created', 'is_verified')
    list_filter = ('owner', 'category', 'is_available', 'date_created', 'is_verified')
    search_fields = ('name', 'description', 'owner__username', 'category__name')
    inlines = [ImageInline]


# Image Admin
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'order_item', 'is_return', 'is_pickup')
    list_filter = ('equipment', 'order_item', 'is_return', 'is_pickup')


# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


# Tag Admin
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Cart Item Inline
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


# Cart Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_created', 'get_cart_total', 'get_cart_items')
    inlines = [CartItemInline]
    readonly_fields = ('get_cart_total', 'get_cart_items')


# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_status', 'date_created', 'date_ordered', 'ordered')
    list_filter = ('status', 'payment_status', 'ordered', 'date_created', 'date_ordered')
    search_fields = ('user__username', 'status', 'payment_status')
    inlines = [OrderItemInline]
    readonly_fields = ('get_order_total', 'get_order_items')


# Order Item Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'order', 'quantity', 'start_date', 'end_date', 'get_order_item_total')
    list_filter = ('order__status', 'order__payment_status', 'start_date', 'end_date')
    search_fields = ('item__name', 'order__user__username')
    readonly_fields = ('get_order_item_total',)


# CartItem Admin (if you want to register it separately)
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'cart', 'quantity', 'start_date', 'end_date', 'get_cart_item_total')
    list_filter = ('start_date', 'end_date')
    search_fields = ('item__name', 'cart__user__username')
    readonly_fields = ('get_cart_item_total',)


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'equipment', 'user', 'rating', 'date_created')
    search_fields = ('equipment__name', 'user__username')
    list_filter = ('rating', 'date_created')


# Specification Admin
@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'name', 'value')
    search_fields = ('equipment__name', 'name', 'value')
    list_filter = ('equipment',)


# Customize Admin Site
admin.site.site_header = "UseNLease Admin"
admin.site.site_title = "UseNLease Equipment Rental Site Admin"
admin.site.index_title = "Welcome to UseNLease Admin Dashboard"