from django.shortcuts import render, get_object_or_404, redirect
from user_management.forms import CheckoutForm
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from user_management.models import Address
from .models import Equipment, Order, OrderItem, Cart, CartItem, Tag, Category, Review
from .serializers import EquipmentSerializer
from django.db.models import Q
from django.db import transaction
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify

import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import EquipmentForm, EquipmentReviewForm

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_payment(request):
    try:
        # Fetch the order to get the total cost
        order = Order.objects.get(user=request.user, ordered=False)
        total = int(order.get_total * 100)

        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=total,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )

        # Begin a transaction to ensure atomicity
        with transaction.atomic():
            # Mark the order as paid and update the ordered status
            order.payment_token = intent.id
            order.payment_status = 'paid'
            order.ordered = True
            order.date_ordered = timezone.now()
            order.save()

            # Iterate over all items in the order and mark their equipment as not available
            for item in order.order_items.all():  # Assuming `order_items` is the related name for OrderItems
                equipment = item.item  # `item` is the foreign key to Equipment in OrderItem
                equipment.is_available = False
                equipment.save()

        return JsonResponse({
            'clientSecret': intent.client_secret,
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def successMsg(request):
    token = request.GET.get('payment_intent')

    if not token:
        return redirect('order_summary')  # Redirect if no token

    try:
        # Find the order using the secure token
        order = Order.objects.get(payment_token=token)
        context = {
            'order': order
        }

        # Mark the order as completed (or whatever your logic is)
        order = Order.objects.get(user=request.user, ordered=False)
        order.status = 'approved'
        order.ordered = True
        order.save()

        return render(request, 'equipment_management/success.html', context)

    except Order.DoesNotExist:
        return redirect('order_summary')  # Redirect if no matching order is found


# def submit_equipment_review(request, equipment_id):
#     equipment = get_object_or_404(Equipment, id=equipment_id)
#     if request.method == 'POST':
#         form = EquipmentReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.equipment = equipment
#             review.user = request.user
#             review.save()
#             return redirect(equipment.get_absolute_url())  # Redirect to equipment detail page
#     else:
#         form = EquipmentReviewForm()
#     return render(request, 'submit_equipment_review.html', {'form': form, 'equipment': equipment})

def submit_owner_review(request, owner_id):
    owner = get_object_or_404(settings.AUTH_USER_MODEL, id=owner_id)
    if request.method == 'POST':
        form = OwnerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = owner
            review.user = request.user
            review.save()
            return redirect('profile_orders')  # Redirect to the orders page
    else:
        form = OwnerReviewForm()
    return render(request, 'submit_owner_review.html', {'form': form, 'owner': owner})

class LatestEquipmentList(APIView):
    def get(self, request, format=None):
        equipments = Equipment.objects.all()[0:4]
        serializer = EquipmentSerializer(equipments, many=True)
        return Response(serializer.data)


def search_view(request):
    query = request.GET.get('query')  # Get the search query from the request
    results = Equipment.objects.all()  # Start with all Equipment objects

    if query:
        # Perform a search on the relevant fields
        results = results.filter(
            Q(name__icontains=query) |  # Search in the name field
            Q(description__icontains=query) |  # Search in the description field
            Q(category__name__icontains=query) |  # Search in the related category's name
            Q(tags__name__icontains=query)  # Search in the related tags' names
        ).distinct()  # Ensure results are distinct to avoid duplicates

    context = {
        'results': results,
        'query': query,
    }
    return render(request, 'equipment_management/search_results.html', context)



def equipment_create_view(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create a new PhysicalAddress from form data
            address = Address.objects.create(
                street_address=data['street_address'],
                street_address2=data.get('street_address2'),
                city=data['city'],
                state=data['state'],
                zip_code=data['zip_code'],
                user=request.user  # Assume the user is the owner of the address
            )

            # Create the Equipment instance
            equipment = Equipment(
                owner=request.user,
                name=data['name'],
                description=data['description'],
                category=data['category'],
                hourly_rate=data['hourly_rate'],
                address=address,
                is_available=data.get('is_available', True),
                terms=data['terms']
            )
            equipment.save()

            # Handle tags
            tags = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                equipment.tags.add(tag)

            messages.success(request, 'Equipment added successfully.')
            return redirect('equipments')  # Redirect to an appropriate page

    else:
        form = EquipmentForm()

    return render(request, 'equipment_management/create_equipment.html', {'form': form})


def cart(request):
    form = EquipmentForm()
    context = {
        'eform': form
    }
    return render(request, 'equipment_management/cart.html', context)


def checkout(request):
    form = EquipmentForm()
    context = {
        'eform': form
    }
    return render(request, 'equipment_management/checkout.html', context)


def home(request):
    trending_ads = Equipment.objects.filter(is_available=True).order_by('-date_created')[:4]  # Fetch trending ads
    equipments = Equipment.objects.all()  # Fetch all equipment
    categories = Category.objects.filter(parent=None)
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Create a new PhysicalAddress from form data
            address = Address.objects.create(
                street_address=data['street_address'],
                street_address2=data.get('street_address2'),
                city=data['city'],
                state=data['state'],
                zip_code=data['zip_code'],
                user=request.user  # Assume the user is the owner of the address
            )

            # Create the Equipment instance
            equipment = Equipment(
                owner=request.user,
                name=data['name'],
                description=data['description'],
                category=data['category'],
                hourly_rate=data['hourly_rate'],
                address=address,
                is_available=data.get('is_available', True),
                terms=data['terms']
            )
            equipment.save()

            # Handle tags
            tags = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                equipment.tags.add(tag)

            messages.success(request, 'Equipment added successfully.')
            return redirect('equipments')  # Redirect to an appropriate page

    else:
        form = EquipmentForm()

    context = {
        'eform': form,
        'categories': categories,
        'equipments': equipments,
        'trending_ads': trending_ads
    }
    return render(request, 'equipment_management/index.html', context)

def about_us(request):
    return render(request, 'equipment_management/about_us.html')

def services(request):
    return render(request, 'equipment_management/services.html')

def service_detail(request):
    return render(request, 'equipment_management/service_detail.html')

def equipment_list(request):
    equipments = Equipment.objects.prefetch_related('images').all()
    categories = Category.objects.filter(parent=None)
    cities = Equipment.objects.values('address__city').annotate(equipment_count=Count('id')).order_by('-equipment_count')

    context = {
        'equipments': equipments,
        'categories': categories,
        'cities': cities,
        'eform': EquipmentForm()
    }
    return render(request, 'equipment_management/categories.html', context)


def equipment_detail(request, slug, id):

    equipment = get_object_or_404(Equipment, slug=slug, id=id)
    if request.method == 'POST':
        form = EquipmentReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.equipment = equipment
            review.user = request.user
            review.save()
            return redirect(equipment.get_absolute_url())  # Redirect to equipment detail page
    else:
        form = EquipmentReviewForm()

    reviews = equipment.reviews.all()


    context = {
        'form': form,
        'equipment': equipment,
        'reviews': reviews
     }

    return render(request, 'equipment_management/equipment_detail.html', context)


# def profile(request):

#     return render(request, 'equipment_management/profile.html')

# def equipment_detail(request, slug, id):
#     equipment = get_object_or_404(Equipment, id=id)

#     related_equipments = Equipment.objects.filter(category=equipment.category)
#     context = {
#         'equipment': equipment,
#         'related_equipments': related_equipments
#     }
#     return render(request, 'equipment_management/equipment_detail.html', context)


def get_or_create_cart(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()  # Ensure the session is created if not present
        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart




def add_to_cart(request, slug, id):
    item = get_object_or_404(Equipment, slug=slug, id=id)
    if request.method == 'POST':
        print(request.POST)

        cart = get_or_create_cart(request)

        # Fetch start_date, end_date, and quantity from the form data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        quantity = int(request.POST.get('quantity'))  # Default to 1 if not provided

        # Try to get an existing cart item or create a new one
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item=item,
            start_date=start_date,
            end_date=end_date,
            quantity=quantity
        )

        if not created:
            # If the cart item already exists, just update the quantity
            cart_item.quantity += quantity
            cart_item.save()
            messages.info(request, 'This item quantity was updated in your cart.')
        else:
            # If a new cart item was created, just save it
            cart_item.save()
            messages.info(request, 'This item was added to your cart.')

    return redirect('cart-summary')


def add_single_item_to_cart(request, slug, id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(Equipment, slug=slug, id=id)

    try:
        cart_item = CartItem.objects.get(
            cart=cart,
            item=item,
            ordered=False
        )
        if cart_item:
            # In the quantity of the item in the cart
            cart_item.quantity += 1
            cart_item.save()
            messages.info(request, 'The quantity of this item was updated.')

    except CartItem.DoesNotExist:
        messages.info(request, 'This item was not in your cart.')

    return redirect('cart-summary')

def remove_from_cart(request, slug, id):
    item = get_object_or_404(Equipment, slug=slug, id=id)
    cart = get_or_create_cart(request)

    try:
        # Retrieve the cart item to be removed
        cart_item = CartItem.objects.get(
            cart=cart,
            item=item,
            ordered=False
        )
        # Remove the cart item from the cart
        cart_item.delete()
        messages.info(request, 'This item was removed from your cart.')
    except CartItem.DoesNotExist:
        messages.info(request, 'This item was not in your cart.')

    return redirect('cart-summary')

def remove_single_item_from_cart(request, slug, id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(Equipment, slug=slug, id=id)

    try:
        cart_item = CartItem.objects.get(
            cart=cart,
            item=item,
            ordered=False
        )
        if cart_item.quantity > 1:
            # Decrease the quantity of the item in the cart
            cart_item.quantity -= 1
            cart_item.save()
            messages.info(request, 'The quantity of this item was updated.')
        else:
            # Remove the item from the cart
            cart_item.delete()
            messages.info(request, 'This item was removed from your cart.')

    except CartItem.DoesNotExist:
        messages.info(request, 'This item was not in your cart.')

    return redirect('cart-summary')


def contact_us(request):
    return render(request, 'equipment_management/contact_us.html')


@login_required
def stripe_view(request):
    if request.method == 'POST':
        print(request.POST)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
    except ObjectDoesNotExist:
        return redirect('cart-summary')
    context = {
        'order': order,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'equipment_management/stripe.html', context)

@login_required
def paypal_view(request):
    return render(request, 'equipment_management/paypal.html')


class CartSummaryView(View):

    def get(self, *args, **kwargs):
        # Get or create a cart based on the session
        session_key = self.request.session.session_key
        if not session_key:
            # Create a session key if it doesn't exist
            self.request.session.save()
            session_key = self.request.session.session_key
        
        try:
            # Retrieve the active cart for the session
            cart = Cart.objects.get(session_key=session_key)

            cart_items = CartItem.objects.filter(id__in=cart.cart_items.values_list('id', flat=True)) \
                                 .select_related('item') \
                                 .prefetch_related('item__images')
            if not cart_items.exists():
                cart.delete()
                return redirect('equipments') 

            context = {
                'cart': cart,
                'cart_items': cart_items,
                'eform': EquipmentForm()
            }
            return render(self.request, 'equipment_management/cart.html', context)

        except ObjectDoesNotExist:
            return redirect('equipments')


def is_valid_form(values):
    return all(field and field.strip() for field in values)



class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            # Try to get the user's active order
            order = Order.objects.get(user=self.request.user, ordered=False)
            print('Got an order')
            print(order.order_items.count)

        except Order.DoesNotExist:
            # If no active order exists, create a new one from the cart
            cart = get_object_or_404(Cart, session_key=self.request.session.session_key)
            if not cart.cart_items.exists():
                messages.info(self.request, "Your cart is empty")
                return redirect('cart')
            
            with transaction.atomic():
                order = Order.objects.create(user=self.request.user, ordered=False)
                print('Created order')
                for item in cart.cart_items.all():
                    OrderItem.objects.create(
                        order=order,
                        item=item.item,
                        quantity=item.quantity,
                        start_date=item.start_date,
                        end_date=item.end_date,
                    )
                cart.delete()  # Remove the cart after creating the order

        form = CheckoutForm()
        context = {
            'form': form,
            'order': order,
            'eform': EquipmentForm()
        }

        # Default shipping address
        shipping_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='S',
            is_default=True
        )
        if shipping_address_qs.exists():
            context['default_shipping_address'] = shipping_address_qs[0]

        # Default billing address
        billing_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='B',
            is_default=True
        )
        if billing_address_qs.exists():
            context['default_billing_address'] = billing_address_qs[0]

        return render(self.request, "equipment_management/checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        is_default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect('checkout')
                else:
                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            street_address2=shipping_address2,
                            country=shipping_country,
                            zip_code=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.is_default = True
                            shipping_address.save()

                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")
                        return redirect('checkout')

                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        is_default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect('checkout')
                else:
                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            street_address2=billing_address2,
                            country=billing_country,
                            zip_code=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.is_default = True
                            billing_address.save()

                    else:
                        messages.info(self.request, "Please fill in the required billing address fields")
                        return redirect('checkout')
                    
                

                # Optionally handle payment options here
                payment_method = form.cleaned_data.get('payment_method')
                print(f"Selected payment method: {payment_method}")  # Debugging line

                if payment_method == 'S':
                    return redirect('stripe') 
                elif payment_method == 'P':
                    return redirect('paypal')
                else:
                    messages.info(self.request, "Please select a payment method")
                    return redirect('checkout')

        except Order.DoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect('checkout')