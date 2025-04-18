# Standard library imports
import json
from datetime import datetime, timedelta


# Django imports
from django.conf import settings
from django.db.models import Sum
from django.db.models import Q
from django.db import transaction

from django.db import transaction
from django.http import JsonResponse, QueryDict
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


# Third-party imports
import stripe
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.pagination import PageNumberPagination


# Local application imports
from .models import Category, Tag, Equipment, Image, Specification, Review, Cart, CartItem, Order, OrderItem
from .serializers import (
    CategorySerializer,
    TagSerializer,
    EquipmentSerializer,
    ImageSerializer,
    SpecificationSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer
)

from .pagination import CustomEquipmentPagination

from user_management.views import JWTAuthenticationFromCookie
from user_management.utils import send_custom_email

# Stripe API Key setup
stripe.api_key = settings.STRIPE_SECRET_KEY

# Other constants
DOMAIN = settings.DOMAIN_URL

from decimal import Decimal


class CreateCheckoutSessionView(APIView):
    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            cart = Cart.objects.get(user=user)

            if not cart.cart_items.exists():
                return Response(
                    {"error": "Cart is empty, cannot create a session."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():  # Ensures atomicity of the order creation process
                # Prepare order data
                cart_items = cart.cart_items.all()
                order_total_price = Decimal(cart.get_cart_total)  # Convert to Decimal
                total_order_items = cart.get_cart_items

                # Create the order
                order_serializer = OrderSerializer(data={
                    'user': user.id,
                    'order_total_price': order_total_price,
                    'total_order_items': total_order_items,
                })
                order_serializer.is_valid(raise_exception=True)
                order = order_serializer.save()

                # Create order items and update inventory
                for cart_item in cart_items:
                    item = cart_item.item
                    if item.available_quantity < cart_item.quantity:
                        return Response(
                            {"error": f"Not enough inventory for {item.name}. Available: {item.available_quantity}, Requested: {cart_item.quantity}"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        item=item,
                        quantity=cart_item.quantity,
                        start_date=cart_item.start_date,
                        end_date=cart_item.end_date,
                    )

                # Calculate service fee (6% of the order total price)
                service_fee = order_total_price * Decimal('0.06')

                # Convert price to cents (including service fee)
                amount_in_cents = int((order_total_price + service_fee) * Decimal('100'))

                stripe_price = stripe.Price.create(
                    unit_amount=amount_in_cents,
                    currency="usd",
                    product_data={
                        "name": f"Order {order.id}",
                    },
                )

                # Create the Stripe session
                session = stripe.checkout.Session.create(
                    mode='payment',
                    customer_email=request.data.get('customer_email'),
                    billing_address_collection='required',
                    shipping_address_collection={'allowed_countries': ['US', 'CA', 'KE']},
                    line_items=[{'price': stripe_price.id, 'quantity': 1}],
                    success_url=f"{settings.DOMAIN_URL}/payment-successful?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
                    cancel_url=f"{settings.DOMAIN_URL}/payment-canceled?order_id={order.id}",
                )

                # Update order with payment details
                order.payment_token = session.id
                order.payment_status = 'pending'
                order.save()

            # --- Prepare Email Contexts with Serializable Data ---

            # For the user email (Order Creation)
            user_email_context = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': getattr(user, 'role', None),
                    'image_url': user.image.url if hasattr(user, 'image') and user.image else None,
                },
                'order': {
                    'id': order.id,
                    'order_total_price': str(order.order_total_price),
                    'total_order_items': order.total_order_items,
                },
                'cart_items': [
                    {
                        'id': cart_item.id,
                        'item': {
                            'id': cart_item.item.id,
                            'name': cart_item.item.name,
                        },
                        'quantity': cart_item.quantity,
                        'start_date': str(cart_item.start_date),
                        'end_date': str(cart_item.end_date),
                    }
                    for cart_item in cart_items
                ],
                'total_price': str(order_total_price + service_fee),
            }
            send_custom_email.delay(
                subject="Order Confirmation - Your Rental Order",
                template_name="emails/order_created.html",
                context=user_email_context,
                recipient_list=[user.email],
            )

            # For equipment owners notification email
            for cart_item in cart_items:
                owner = cart_item.item.owner
                owner_email_context = {
                    'owner': {
                        'id': owner.id,
                        'username': owner.username,
                        'email': owner.email,
                    },
                    'item': {
                        'id': cart_item.item.id,
                        'name': cart_item.item.name,
                    },
                    'renter': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                    },
                    'quantity': cart_item.quantity,
                    'start_date': str(cart_item.start_date),
                    'end_date': str(cart_item.end_date),
                }
                send_custom_email.delay(
                    subject=f"Equipment Rental Notification - {cart_item.item.name}",
                    template_name="emails/equipment_rented.html",
                    context=owner_email_context,
                    recipient_list=[owner.email],
                )

            return Response(
                {
                    'session_id': session.id,
                    'url': session.url,
                    'order_id': order.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Cart.DoesNotExist:
            return Response({"error": "No cart found for the user"}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SessionStatusView(APIView):
    """
    Retrieves the status of a Stripe checkout session.
    """

    authentication_classes = [JWTAuthentication]  # Adjusted to match the JWTAuthentication class name
    permission_classes = [AllowAny]  # Allow unauthenticated users to access

    def get(self, request):
        session_id = request.query_params.get('session_id')

        if not session_id:
            return Response(
                {'error': 'Session ID is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Retrieve Stripe session details
            session = stripe.checkout.Session.retrieve(session_id)

            with transaction.atomic():  # Ensure all database updates are atomic
                # Attempt to find the order associated with this session
                order = Order.objects.filter(payment_token=session_id).first()

                if not order:
                    return Response(
                        {'error': 'Order not found for the given session ID.'},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Mark the order as paid
                order.payment_status = 'paid'
                order.ordered = True
                order.date_ordered = datetime.now()
                order.save()

                # Clear the cart after the payment is successful
                cart = Cart.objects.filter(user=order.user).first()  # Retrieve the cart for the user
                if cart:
                    cart.cart_items.all().delete()  # Delete all items in the cart

            # Build the response with session and order details
            status_response = {
                'session_status': session.status,
                'payment_status': order.payment_status,
                'customer_email': session.customer_details.email if session.customer_details else None,
                'order_id': order.id,
                'order_total_price': order.order_total_price,
                'total_order_items': order.total_order_items,
            }

            return Response(status_response, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Stripe error: {e.user_message}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def convert_querydict_to_dict(querydict):
    """
    Converts a QueryDict to a regular dictionary, handling specific field 
    conversions such as address and tags serialized as JSON strings.
    """
    result = {}

    for key, value in querydict.lists():
        # If there's only one item in the value list, unpack it
        if len(value) == 1:
            result[key] = value[0]
        else:
            result[key] = value

    # Handle specific conversions for 'address' and 'tags'
    if 'address' in result and isinstance(result['address'], list):
        # Convert the 'address' list to a dictionary if nested
        result['address'] = {
            'street_address': result['address'][0].get('street_address', [])[0],
            'city': result['address'][0].get('city', [])[0],
            'state': result['address'][0].get('state', [])[0],
            'zip_code': result['address'][0].get('zip_code', [])[0],
            'country': result['address'][0].get('country', [])[0]
        }

    if 'tags' in result:
        try:
            # Safely parse the tags JSON string to a Python list
            result['tags'] = json.loads(result['tags'])
        except (json.JSONDecodeError, TypeError) as e:
            return Response(f"error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

    return result


class CategoryViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        List all categories.
        """
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new category.
        """
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific category by primary key.
        """
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update an existing category.
        """
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a category.
        """
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        category = Category.objects.get(pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RootCategoryListView(generics.ListAPIView):
    """
    List root categories (categories with no parent).
    """
    serializer_class = CategorySerializer

    def get_queryset(self):
        """
        Return root categories (categories without parent).
        """
        return Category.objects.filter(parent__isnull=True)


class TagViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        """
        List all tags.
        """
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new tag.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied

        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific tag by primary key.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied

        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update an existing tag.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied

        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a tag.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied

        tag = Tag.objects.get(pk=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Equipment objects.
    Provides list, create, retrieve, and update actions.
    """
    
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    authentication_classes = [JWTAuthenticationFromCookie]
    pagination_class = CustomEquipmentPagination  # Use custom pagination


    def get_permissions(self):
        """
        Override permissions to allow unauthenticated access to list and retrieve,
        but require authentication for create, update, and delete.
        """
        if self.action in ["list", "retrieve", "filter", "related"]:
            return [AllowAny()]  # No authentication required for viewing equipment
        return [IsAuthenticated()]  # Authentication required for create, update, delete

    def list(self, request):
        """
        List all verified equipment with pagination.
        """
        queryset = self.filter_queryset(self.get_queryset().filter(is_verified=True))  # Filter only verified items
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    @action(detail=False, methods=["GET"], url_path="filter")
    def filter(self, request):
        """
        Custom filtering action for searching and filtering by category, tags, and city.
        - `category`: Filter by a single category (ID or name, optional)
        - `categories`: Filter by multiple categories (comma-separated slugs, optional)
        - `search`: Search in name, description, and tags (optional)
        - `city`: Filter by a single city (optional)
        - `cities`: Filter by multiple cities (comma-separated slugs, optional)
        """
        queryset = Equipment.objects.filter(is_verified=True)

        # Get query parameters
        category = request.GET.get("category")
        search = request.GET.get("search")
        city = request.GET.get("city")
        categories = request.GET.get("categories", "").split(",") if request.GET.get("categories") else []
        cities = request.GET.get("cities", "").split(",") if request.GET.get("cities") else []

        # Filter by single category (ID or slug)
        if category:
            if category.isdigit():
                queryset = queryset.filter(category_id=int(category))
            else:
                queryset = queryset.filter(category__slug__icontains=category)

        # Filter by multiple categories (slugified)
        if categories:
            queryset = queryset.filter(category__slug__in=categories)

        # Filter by single city
        if city:
            queryset = queryset.filter(address__city__icontains=city)

        # Filter by multiple cities
        if cities:
            print("cities", cities)
            queryset = queryset.filter(address__city__in=cities)

        # Apply search if provided
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                # Q(description__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()

        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            if not page:  # Check if the page is empty
                return Response({"message": "No equipment found for the given filters"}, status=200)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)
    
    @action(detail=True, methods=["GET"], url_path="related")
    def related(self, request, pk=None):
        """
        Retrieve related equipment items based on the same category.
        """
        try:
            equipment = self.get_object()
            related_items = Equipment.objects.filter(
                category=equipment.category
            ).exclude(id=equipment.id)[:12]  # Limit to 12 items

            serializer = self.get_serializer(related_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Equipment.DoesNotExist:
            return Response({"detail": "Equipment not found."}, status=status.HTTP_404_NOT_FOUND)

    

    def create(self, request, *args, **kwargs):
        """
        Create a new equipment item.
        Handles file uploads and data processing.
        """
        try:
            with transaction.atomic():  # Ensures all operations are atomic
                # Handle images if provided in the 'images' key
                images = request.FILES.getlist('images')

                # Convert incoming querydict to a structured dictionary
                data = convert_querydict_to_dict(request.data)

                # Group address fields into a dictionary
                address = {
                    'street_address': data.pop('street_address', None),
                    'city': data.pop('city', None),
                    'state': data.pop('state', None),
                    'zip_code': data.pop('zip_code', None),
                    'country': data.pop('country', None)
                }
                data['address'] = address

                terms = data.pop('terms', None)
                if terms:
                    data['terms'] = terms

                # Convert tags to a list of Tag instances (or create them if they don't exist)
                tags_input = data.pop('tags', [])
                tags = []
                for tag_name in tags_input:
                    tag, created = Tag.objects.get_or_create(name=tag_name.strip())  # Get or create tag
                    tags.append(tag)

                # Convert specifications from string to list of dictionaries
                if 'specifications' in data:
                    specifications_data  = json.loads(data.pop('specifications'))

                # Initialize and validate the equipment serializer
                serializer = self.get_serializer(data=data, context={'request': request})
                serializer.is_valid(raise_exception=True)

                # Save the equipment instance
                equipment = serializer.save(terms=terms)

                for spec in specifications_data:
                    # Rename 'key' to 'name' in the specification data
                    if 'key' in spec:
                        spec['name'] = spec.pop('key', None)

                    # Ensure 'name' is present
                    if not spec.get('name'):
                        return Response({'detail': 'Specification name is required.'}, status=status.HTTP_400_BAD_REQUEST)

                    # Create or retrieve Specification model instance
                    specification_instance, created = Specification.objects.get_or_create(
                        name=spec['name'],
                        defaults={'value': spec.get('value')},  # Include other fields as needed
                        equipment=equipment
                    )

                # Handle images if necessary
                if images:
                    for image in images:
                        equipment.images.create(image=image)

                # Set the tags after saving the equipment
                if tags:
                    equipment.tags.set(tags)

            # Return the created equipment data
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        """
        Retrieve a specific equipment item by primary key.
        Includes booked dates.
        """
        equipment = Equipment.objects.get(pk=pk)
        
        # Get booked dates for this equipment
        booked_dates = OrderItem.objects.filter(item=equipment).values("start_date", "end_date")


        # Serialize the equipment data
        serializer = EquipmentSerializer(equipment)
        
        # Add booked dates to the response
        response_data = serializer.data
        response_data["booked_dates"] = list(booked_dates)

        return Response(response_data)

    
    

    def update(self, request, pk=None):
        """
        Update an existing equipment item.
        Handles images and category updates.
        """
        self.check_permissions(request)

        # Retrieve the existing equipment instance or raise 404 error
        equipment = get_object_or_404(Equipment, pk=pk)
        data = request.data

        try:
            with transaction.atomic():  # Ensures atomicity
                # Handle images if provided
                images = request.FILES.getlist('images')
                if images:
                    # Clear existing images
                    equipment.images.all().delete()

                    # Add new images
                    for image in images:
                        equipment.images.create(image=image)

                # Handle multipart/form-data query dict
                if isinstance(data, QueryDict):
                    data = data.dict()

                # Resolve category if provided
                if 'category' in data:
                    category_instance = get_object_or_404(Category, id=data.get('category'))
                    data['category'] = category_instance.id  # Replace with valid category ID

                # Perform partial updates
                serializer = EquipmentSerializer(equipment, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class UserEquipmentView(APIView):
    """
    Custom API to get equipment for a specific authenticated user.
    """

    # Specify the authentication class
    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        """
        List all equipment for the logged-in user.
        If no equipment is found, return a message indicating no equipment available.
        """
        user = request.user

        # If user is authenticated (IsAuthenticated permission checks this)
        if not user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Filter equipment based on the logged-in user
        queryset = Equipment.objects.filter(owner=user)


        if not queryset.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)  # No Content

        # Serialize the queryset and return data
        serializer = EquipmentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserEditableEquipmentView(APIView):
    """
    API to get the IDs of equipment for a specific authenticated user
    that are not ordered (is_ordered=False) and are not part of any order item.
    """

    # Specify the authentication class
    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, *args, **kwargs):
        """
        Return the IDs of all equipment for the logged-in user
        that are not ordered and are not part of any order item.
        """
        user = request.user

        # If user is not authenticated
        if not user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get all equipment owned by the user
        queryset = Equipment.objects.filter(owner=user)

        # Exclude equipment that is part of an order item
        ordered_equipment_ids = OrderItem.objects.all().values_list('item_id', flat=True)
        queryset = queryset.exclude(id__in=ordered_equipment_ids)

        # Extract the IDs from the filtered queryset (ensure it's flat)
        equipment_ids = list(queryset.values_list('id', flat=True))


        if not equipment_ids:
            return Response(status=status.HTTP_204_NO_CONTENT)  # No Content

        # Return the IDs as a list
        return Response(equipment_ids, status=status.HTTP_200_OK)




class ImageViewSet(viewsets.ViewSet):
    """
    ViewSet for handling image-related actions such as listing, creating, 
    retrieving, updating, and deleting images.
    """
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        List all images. Requires admin user permissions.
        """
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Image.objects.all()
        serializer = ImageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new image. Requires authenticated user permissions.
        """
        # Uncomment to enforce permission check for authenticated users
        # self.permission_classes = [permissions.IsAuthenticated]
        # self.check_permissions(request)

        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific image by primary key. Requires authenticated user.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)
        serializer = ImageSerializer(image)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update an existing image by primary key. Requires authenticated user.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)
        serializer = ImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete an image by primary key. Requires authenticated user.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    
class SpecificationViewSet(viewsets.ViewSet):
    """
    ViewSet for handling specification-related actions such as listing, 
    creating, retrieving, updating, and deleting specifications.
    """
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        List all specifications. Requires admin user permissions.
        """
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Specification.objects.all()
        serializer = SpecificationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new specification. Requires authenticated user permissions.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        serializer = SpecificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific specification by primary key. Requires authenticated user.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)
        serializer = SpecificationSerializer(specification)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update an existing specification by primary key. Requires authenticated user.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)
        serializer = SpecificationSerializer(specification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a specification by primary key. Requires authenticated user.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)
        specification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(viewsets.ViewSet):
    """
    ViewSet for handling review-related actions such as listing, creating, 
    retrieving, updating, and deleting reviews.
    """
    authentication_classes = [JWTAuthenticationFromCookie]
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        List all reviews with non-null, non-empty review_text.
        """
        queryset = Review.objects.filter(review_text__isnull=False).exclude(review_text="")
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        """
        Create a new review. The equipment being reviewed must be in a completed order of the user.
        """
        user = request.user
        data = request.data.copy()
        equipment_id = data.get("equipment")  # Ensure "equipment" is passed in request data

        if not equipment_id:
            return Response(
                {"error": "Equipment ID is required to leave a review."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has a completed order item for the specified equipment
        has_completed_order_item = OrderItem.objects.filter(
            order__user=user, status="completed", item_id=equipment_id
        ).exists()

        if not has_completed_order_item:
            return Response(
                {"error": "You can only leave a review for equipment you have ordered and completed."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Attach the user ID to request data before validation
        data["user"] = user.id  

        try:
            with transaction.atomic():  # Ensures atomicity
                serializer = ReviewSerializer(data=data)
                if serializer.is_valid():
                    serializer.save(user=user)  
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific review by primary key.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)
        review = Review.objects.get(pk=pk)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update an existing review.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)
        review = Review.objects.get(pk=pk)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a review.
        """
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)
        review = Review.objects.get(pk=pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling cart-related actions such as listing, creating, 
    updating, and deleting carts. Only authenticated users can access their carts.
    """
    authentication_classes = [JWTAuthenticationFromCookie]
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return the user's cart. If no cart exists, create one.
        """
        Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(user=self.request.user)


    def create(self, request, *args, **kwargs):
        """
        Create a cart for the logged-in user. If the user is a 'lessor', raise a permission error.
        """
        user = request.user

        # Check if the user has the 'lessor' role
        if user.role == 'lessor':  # Replace 'lessor' with the actual role name if different
            raise PermissionDenied("You are a lessor!")

        try:
            with transaction.atomic():  # Ensures atomicity
                # Get or create a cart for the user
                cart, created = Cart.objects.get_or_create(user=user)

                if not created:
                    # If the cart already exists, return its details with a custom message
                    serializer = self.get_serializer(cart)
                    return Response(
                        {"detail": "A cart already exists for this user.", "cart": serializer.data},
                        status=status.HTTP_200_OK
                    )

                # If a new cart is created, return its details in the response
                serializer = self.get_serializer(cart)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    def update(self, request, *args, **kwargs):
        """
        Update the user's cart. If the user is a 'lessor', raise a permission error.
        """
        user = request.user

        # Check if the user has the 'lessor' role
        if user.role == 'lessor':  # Replace 'lessor' with the actual role name if different
            raise PermissionDenied("You are a lessor!")

        # Ensure a cart exists for the user before updating
        cart = self.get_object()
        serializer = self.get_serializer(cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete the user's cart. If the cart exists, remove it from the database.
        """
        cart = self.get_object()
        cart.delete()
        return Response({"detail": "Cart deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling cart item actions such as listing, creating, 
    updating, and deleting cart items. Only authenticated users can 
    access their cart items.
    """
    authentication_classes = [JWTAuthenticationFromCookie]
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_cart_item(self):
        """
        Return the cart item based on the provided ID in the request data.
        """
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.get(id=self.request.data.get('id'))

    def get_queryset(self):
        """
        Return the user's cart items.
        """
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=user_cart)
    

    def create(self, request, *args, **kwargs):
        """
        Create a new cart item for the logged-in user. Ensure the user is not leasing their own equipment.
        """
        user = request.user

        # Check if the user is a 'lessor'
        if user.role == 'lessor':
            raise PermissionDenied("Lessors cannot add items to the cart!")

        try:
            with transaction.atomic():  # Ensures atomicity
                user_cart, _ = Cart.objects.get_or_create(user=user)
                
                item_data = request.data
                item_id = item_data.get("item")  # Get the item ID
                item_quantity = item_data.get("quantity", 1)

                # Ensure valid dates
                new_start_date = datetime.strptime(item_data.get("start_date"), "%Y-%m-%d").date()
                new_end_date = datetime.strptime(item_data.get("end_date"), "%Y-%m-%d").date()

                # Get the equipment
                try:
                    equipment = Equipment.objects.get(id=item_id)
                except Equipment.DoesNotExist:
                    return Response({"error": "Equipment not found."}, status=status.HTTP_404_NOT_FOUND)

                # Prevent the owner from leasing their own equipment
                if equipment.owner == user:
                    raise PermissionDenied("You cannot rent your own Item!")

                # Check **future bookings** for the same equipment in the requested period
                overlapping_bookings = OrderItem.objects.filter(
                    item=equipment,
                    start_date__lt=new_end_date,  # Overlaps requested period
                    end_date__gt=new_start_date
                )

                # Calculate the **daily available quantity** by checking existing bookings
                date_cursor = new_start_date
                while date_cursor < new_end_date:
                    # Sum all booked quantities for this specific day
                    booked_quantity_on_day = overlapping_bookings.filter(
                        start_date__lte=date_cursor,
                        end_date__gt=date_cursor
                    ).aggregate(total_booked=Sum("quantity"))["total_booked"] or 0

                    available_on_day = equipment.available_quantity - booked_quantity_on_day

                    if available_on_day < item_quantity:
                        return Response(
                            {
                                "error": f"Only {available_on_day} units are available on {date_cursor}. "
                                        "Your booking would exceed the available stock."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    date_cursor += timedelta(days=1)  # Move to the next day

                # Check if the item already exists in the cart
                existing_cart_item = CartItem.objects.filter(cart=user_cart, item_id=item_id).first()

                if existing_cart_item:
                    existing_start_date = existing_cart_item.start_date
                    existing_end_date = existing_cart_item.end_date

                    if existing_start_date != new_start_date or existing_end_date != new_end_date:
                        existing_cart_item.quantity = item_quantity
                        existing_cart_item.start_date = new_start_date
                        existing_cart_item.end_date = new_end_date
                    else:
                        existing_cart_item.quantity += item_quantity

                    existing_cart_item.save()
                    serializer = self.get_serializer(existing_cart_item)
                    return Response(serializer.data, status=status.HTTP_200_OK)

                # Create a new cart item
                item_data['cart'] = user_cart.id  
                serializer = self.get_serializer(data=item_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def update(self, request, *args, **kwargs):
        """
        Update an existing cart item by checking the available quantity and date availability.
        """
        try:
            with transaction.atomic():  # Ensures atomicity
                cart_item = self.get_cart_item()
                item_data = request.data

                # Get the updated item quantity from the request data
                item_quantity = item_data.get("quantity", cart_item.quantity)

                # Get the updated start and end dates from the request data
                start_date = item_data.get("start_date", cart_item.start_date)
                end_date = item_data.get("end_date", cart_item.end_date)

                # Get the equipment object associated with the cart item
                equipment = cart_item.item

                # Check if available quantity is sufficient for the date range
                available_quantity = equipment.get_available_quantity(start_date, end_date)

                if available_quantity < item_quantity:
                    return Response(
                        {"error": f"Only {available_quantity} items are available for the selected date range."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Update the cart item with the new quantity and dates
                cart_item.quantity = item_quantity
                cart_item.start_date = start_date
                cart_item.end_date = end_date
                cart_item.save()

                # Return the updated cart item as a response
                serializer = self.get_serializer(cart_item)
                return Response(serializer.data)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        """
        Delete an existing cart item.
        """
        cart_item = self.get_object()
        cart_item.delete()
        return Response({"detail": "Cart item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class OrderActionView(APIView):
    """
    View for handling various actions on an order, such as terminating, 
    deleting, or reordering the order. Only authenticated users can 
    perform these actions on their orders.
    """
    authentication_classes = [JWTAuthenticationFromCookie]

    def post(self, request, pk, action):
        """
        Handle order actions like terminate, delete, or reorder.
        Each action corresponds to a specific modification to the order.
        """
        try:
            with transaction.atomic():  # Ensures atomicity
                # Fetch the order object associated with the user
                order = Order.objects.get(id=pk, user=request.user)

                # Handle the corresponding action
                if action == 'terminate':
                    order.terminate_rental()
                else:
                    return Response(
                        {'error': 'Invalid action'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Return success message after action
                return Response(
                    {'message': f'Order {action} action successful'},
                    status=status.HTTP_200_OK
                )

        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        self.check_permissions(request)
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.check_permissions(request)

        try:
            with transaction.atomic():  # Ensures atomicity
                cart = Cart.objects.get(user=request.user)
                cart_items = cart.cart_items.all()

                if not cart_items.exists():
                    return Response({"error": "Cart is empty, cannot create an order"}, status=status.HTTP_400_BAD_REQUEST)

                # Calculate order totals
                order_total_price = Decimal(sum(item.quantity * item.item.hourly_rate for item in cart_items))
                total_order_items = sum(item.quantity for item in cart_items)
                service_fee = (order_total_price * Decimal('0.06')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                order_total_price_with_fee = (order_total_price + service_fee).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                # Validate inventory before proceeding
                for cart_item in cart_items:
                    if cart_item.item.available_quantity < cart_item.quantity:
                        return Response({
                            "error": f"Not enough stock for {cart_item.item.name}. Available: {cart_item.item.available_quantity}, Requested: {cart_item.quantity}"
                        }, status=status.HTTP_400_BAD_REQUEST)

                # Create order
                order = Order.objects.create(
                    user=request.user,
                    order_total_price=order_total_price_with_fee,
                    total_order_items=total_order_items,
                    payment_status='pending'
                )

                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        item=cart_item.item,
                        quantity=cart_item.quantity,
                        start_date=cart_item.start_date,
                        end_date=cart_item.end_date
                    )

                return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({"error": "No cart found for the user"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_order(self, pk, user):
        """Helper function to retrieve an order object with permission check"""
        return get_object_or_404(Order, id=pk, user=user)
    



    
class OrderItemViewSet(viewsets.ViewSet):
    """
    A viewset for listing, creating, retrieving, updating, and deleting order items.
    Only authenticated users can access and modify their order items.
    """
    authentication_classes = [JWTAuthenticationFromCookie]

    def get_permissions(self):
        """Override permissions for specific methods."""
        if self.action == "list_booked_items":
            return [permissions.AllowAny()]  # No authentication required
        return [permissions.IsAuthenticated()]  # Authentication required for all other methods
    
    def get_order_item(self, pk, user):
        """
        Retrieve a specific OrderItem by ID and ensure the user has permission to access it.
        """
        try:
            order_item = OrderItem.objects.get(pk=pk)

            # Ensure the user is either the item owner or the lessor
            if order_item.item.owner != user and order_item.order.lessor != user:
                raise PermissionDenied("You do not have permission to access this order item.")

            return order_item
        except OrderItem.DoesNotExist:
            return Response(
                {"error": "Order Item not found!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a rental request for an order item.
        Only the owner of the item can approve.
        """
        with transaction.atomic():  # Ensures atomicity
            order_item = get_object_or_404(OrderItem, id=pk)

            # Check if the logged-in user is the owner of the item
            if order_item.item.owner.id != request.user.id:
                return Response(
                    {"error": "You are not authorized to approve this item."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Ensure the order item is still pending
            if order_item.status != 'pending':
                return Response(
                    {"error": "Only pending items can be approved."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Approve the order item
            order_item.status = 'approved'
            order_item.save()

            # Check if all order items in the order are approved
            order = order_item.order
            if all(item.status == 'approved' for item in order.order_items.all()):
                order.status = 'approved'
                order.save()

            else:
                order.status = 'partially_approved'
                order.save()

            return Response({"message": "Order item approved successfully"}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def initiate_pickup(self, request, pk=None):
        """
        Lessee initiates pickup by providing images and identity document.
        """
        with transaction.atomic():  # Ensures atomicity
            order_item = get_object_or_404(OrderItem, id=pk)

            if order_item.status != 'approved':
                return Response({"error": "Order item must be approved to initiate pickup"}, status=status.HTTP_400_BAD_REQUEST)

            pickup_images = request.FILES.getlist('pickup_images')
            identity_document_type = request.data.get('documentType')

            if len(pickup_images) > 3:
                return Response({"error": "Too many pickup images"}, status=status.HTTP_400_BAD_REQUEST)

            if identity_document_type not in ['id', 'dl', 'passport']:
                return Response({"error": "Invalid identity document type"}, status=status.HTTP_400_BAD_REQUEST)

            # Save images linked to this order item
            for image in pickup_images:
                Image.objects.create(order_item=order_item.order, equipment_id=order_item.item.id, image=image, is_pickup=True)

            order_item.identity_document_type = identity_document_type
            order_item.status = 'pickup'
            order_item.save()

            return Response({"message": "Pickup initiated successfully"}, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['post'])
    def initiate_return(self, request, pk=None):
        """
        Lessee initiates return by providing identity document type.
        """
        with transaction.atomic():  # Ensures atomicity
            order_item = get_object_or_404(OrderItem, id=pk)

            if order_item.status != 'rented':
                return Response({"error": "Order item must be rented to initiate return"}, status=status.HTTP_400_BAD_REQUEST)

            order_item.status = 'return'
            order_item.save()

            return Response({"message": "Return initiated successfully"}, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['post'])
    def confirm_pickup(self, request, pk=None):
        """
        Lessor confirms pickup for all order items in the same order that are in the 'pickup_initiated' stage.
        Stores the captured ID document for each order item.
        """
        with transaction.atomic():  # Ensures atomicity
            # Get the specific order item to identify the parent order
            order_item = self.get_order_item(pk, request.user)
            order = order_item.order  # Assuming order_item has a ForeignKey to Order

            # Check if an ID document image was uploaded
            id_image = request.FILES.get("id_image")
            if not id_image:
                return Response({"error": "ID document image is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Get all order items in the same order that are in 'pickup_initiated' status
            order_items = order.order_items.filter(status='pickup')  # Assuming order_items is the related name

            if not order_items.exists():
                return Response({"error": "No order items are in the pickup initiated stage"}, status=status.HTTP_400_BAD_REQUEST)

            # Process each order item
            updated_items = []
            for item in order_items:
                # Save the ID document image for each order item
                item.identity_document_image.save(id_image.name, id_image, save=False)
                if not item.identity_document_image:
                    return Response({"error": f"Failed to save ID document image for order item {item.id}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Update status to 'rented'
                item.status = 'rented'
                item.save()
                updated_items.append({
                    "order_item_id": item.id,
                    "image_url": item.identity_document_image.url
                })

            # Check if all items in the order are now 'rented' to update the order status
            all_rented = order.order_items.all().count() == order.order_items.filter(status='rented').count()
            if all_rented:
                order.status = 'rented'
            else:
                order.status = 'partially_rented'
            order.save()

            return Response({
                "message": "Pickup confirmed successfully for all eligible order items",
                "updated_items": updated_items
            }, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['post'])
    def confirm_return(self, request, pk=None):
        """
        Lessor confirms return. If the item is damaged, it cannot be marked as completed.
        """
        with transaction.atomic():  # Ensures atomicity
            order_item = self.get_order_item(pk, request.user)

            if order_item.status not in ['return']:
                return Response({"error": "Item return must be initiated first"}, status=status.HTTP_400_BAD_REQUEST)

            # Get return condition and complaint details from request with safe default values
            return_condition = request.data.get("returnCondition", "").strip().lower() if request.data.get("returnCondition") else "good"
            complaint_text = request.data.get("complaintText", "").strip() if request.data.get("complaintText") else ""

            # Validate return condition
            if return_condition not in ["good", "damaged"]:
                return Response(
                    {"error": "Invalid return condition. Must be either 'good' or 'damaged'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save return condition to the order item
            order_item.return_item_condition = return_condition

            if return_condition == "damaged":
                # If damaged, require a complaint
                if not complaint_text:
                    return Response(
                        {"error": "A complaint description is required if the item is damaged."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Store complaint text and mark as disputed (NOT completed)
                order_item.return_item_condition_custom = complaint_text
                order_item.status = "disputed"
                order_item.save()
                
                # Update order status based on all items
                order = order_item.order
                all_items_status = order.order_items.values_list('status', flat=True)
                if all(status in ['completed', 'disputed'] for status in all_items_status):
                    order.status = 'returned'
                else:
                    order.status = 'partially_returned'
                order.save()

                return Response({
                    "message": "Item return recorded as damaged. Complaint noted.",
                    "return_condition": return_condition,
                    "complaint": complaint_text,
                    "status": "disputed",
                }, status=status.HTTP_200_OK)
            
            # If return condition is good, mark as completed
            order_item.status = "completed"
            order_item.save()

            # Update order status based on all items
            order = order_item.order
            all_items_status = order.order_items.values_list('status', flat=True)
            if all(status in ['completed', 'disputed'] for status in all_items_status):
                order.status = 'returned'
            else:
                order.status = 'partially_returned'
            order.save()

            return Response({
                "message": "Item return confirmed successfully.",
                "return_condition": return_condition,
                "status": "completed",
            }, status=status.HTTP_200_OK)


    def list(self, request):
        """
        List all order items where the item owner is the logged-in user.
        """
        self.check_permissions(request)  # Ensure permission check is applied

        # Filter order items where the item owner is the logged-in user
        queryset = OrderItem.objects.filter(item__owner_id=request.user.id)

        serializer = OrderItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    def create(self, request):
        """
        Create a new order item.
        """
        self.check_permissions(request)  # Ensure permission check is applied

        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific order item by its ID.
        """
        self.check_permissions(request)  # Ensure permission check is applied

        try:
            order_item = OrderItem.objects.get(pk=pk, user=request.user)
        except OrderItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update an existing order item.
        """
        self.check_permissions(request)  # Ensure permission check is applied

        try:
            order_item = OrderItem.objects.get(pk=pk)
        except OrderItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderItemSerializer(order_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete an order item.
        """
        self.check_permissions(request)  # Ensure permission check is applied

        try:
            order_item = OrderItem.objects.get(pk=pk)
        except OrderItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    def list_booked_items(self, request, pk):
        """
        Retrieve the booked items along with their quantities and dates for a specific item.
        Also, return the total number of items booked.
        """

        try:
            # Fetch order items for the given item ID (pk), ensuring end_date is not in the past
            order_items = OrderItem.objects.filter(item_id=pk, end_date__gte=now().date())

            # Compute the total number of booked items for the specific item
            total_booked_quantity = order_items.aggregate(total=Sum('quantity'))['total'] or 0

            # Dictionary to store grouped bookings by (start_date, end_date)
            grouped_bookings = {}

            for order_item in order_items:
                date_range_key = (order_item.start_date, order_item.end_date)

                if date_range_key in grouped_bookings:
                    # If the date range already exists, add the quantity
                    grouped_bookings[date_range_key]["quantity"] += order_item.quantity
                else:
                    # Otherwise, create a new entry
                    grouped_bookings[date_range_key] = {
                        "quantity": order_item.quantity,
                        "start_date": order_item.start_date,
                        "end_date": order_item.end_date,
                    }

            # Convert dictionary values to a list for response
            booked_items_data = list(grouped_bookings.values())

            # Return both the list of booked items and the total quantity
            return Response({
                "total_booked": total_booked_quantity,  # Total items booked for this specific item
                "booked_dates": booked_items_data      # Booked items with their start and end dates
            }, status=status.HTTP_200_OK)

        except OrderItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
