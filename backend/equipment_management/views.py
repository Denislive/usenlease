# rentals/views.py
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError



from django.http import JsonResponse
from django.db import transaction
import json
from datetime import datetime
from django.conf import settings
from rest_framework import generics

from django.http import QueryDict

from rest_framework import status
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

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

DOMAIN = 'http://localhost:3000'
class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        # Retrieve the access and refresh tokens from cookies
        access_token = request.COOKIES.get('token')  # Access token cookie
        refresh_token = request.COOKIES.get('refresh')  # Refresh token cookie
        
        # If no access token is present, return None (unauthenticated)
        if not access_token:
            return None

        try:
            # Try to validate the access token
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            # If the access token is expired or invalid, attempt to refresh using the refresh token
            if refresh_token:
                try:
                    # Attempt to get a new access token using the refresh token
                    refresh = RefreshToken(refresh_token)
                    new_access_token = str(refresh.access_token)

                    # Set the new access token in the cookies (or headers as needed)
                    response = self.get_user_response(request)
                    response.set_cookie('token', new_access_token, httponly=True, secure=True)
                    
                    # Validate the new access token
                    validated_token = self.get_validated_token(new_access_token)
                    return self.get_user(validated_token), validated_token
                except TokenError as e:
                    # If refreshing the token fails, raise an authentication error
                    raise AuthenticationFailed(_('Token is invalid or expired.'))

            # If no refresh token is available, raise an authentication error
            raise AuthenticationFailed(_('Token is expired and no refresh token is provided.'))

    def get_user_response(self, request):
        """
        Helper method to return the response object where the new access token can be set.
        """
        # The `request` object doesn't provide response, this method is just an example.
        # You can adjust this method to work with your response handling logic.
        from rest_framework.response import Response
        return Response()
   

class CreateCheckoutSessionView(APIView):
    """
    Handles the creation of a Stripe checkout session and order creation.
    """

    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [permissions.IsAuthenticated]  # Restrict access to authenticated users

    def post(self, request):
        try:
            # Get the user and their associated cart
            user = request.user
            cart = Cart.objects.get(user=user)

            # If the cart is empty, return an error
            if not cart.cart_items.exists():
                return Response({"error": "Cart is empty, cannot create a session."}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare order data
            cart_items = cart.cart_items.all()
            order_total_price = cart.get_cart_total
            total_order_items = cart.get_cart_items

            # Create the order using a serializer
            order_serializer = OrderSerializer(data={
                'user': user.id,
                'order_total_price': order_total_price,
                'total_order_items': total_order_items,
            })
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save()

            # Create order items for each item in the cart
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    start_date=cart_item.start_date,
                    end_date=cart_item.end_date,
                )

            # Convert price to cents for Stripe
            amount_in_cents = int(order_total_price * 100)

            # Prepare item details for the Stripe session
            items_list = [
                {
                    "name": item.item.name,
                    "quantity": item.quantity,
                    "start_date": str(item.start_date),
                    "end_date": str(item.end_date),
                    "hourly_rate": float(item.item.hourly_rate),
                    "total": float(item.total),
                }
                for item in order.order_items.all()
            ]

            # Create a price object in Stripe
            stripe_price = stripe.Price.create(
                unit_amount=amount_in_cents,
                currency="usd",
                product_data={
                    "name": f"Order {order.id}",
                },
                metadata={
                    "order_summary": f"Order total items: {order.total_order_items} --- Order total Price: ${order.order_total_price}",
                    "items": json.dumps(items_list),  # Serialize items as JSON string
                },
            )

            # Create a Stripe checkout session
            session = stripe.checkout.Session.create(
                mode='payment',
                customer_email=request.data.get('customer_email'),
                billing_address_collection='required',
                shipping_address_collection={'allowed_countries': ['US', 'CA', 'KE']},
                line_items=[{'price': stripe_price.id, 'quantity': 1}],
                success_url=f"{DOMAIN}/payment-successful?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{DOMAIN}/payment-canceled",
            )

            # Update order with payment details
            order.payment_token = session.id
            order.payment_status = 'pending'
            order.save()

            # Clear the cart
            cart_items.delete()

            return Response({
                'session_id': session.id,
                'url': session.url,
                'order_id': order.id,
            }, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return Response({"error": "No cart found for the user"}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SessionStatusView(APIView):
    """
    Retrieves the status of a Stripe checkout session.
    """

    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [AllowAny]  # Allow unauthenticated users to access

    def get(self, request):
        # Get the session ID from query params
        session_id = request.query_params.get('session_id')

        # If no session ID is provided, return an error
        if not session_id:
            return Response({'error': 'Session ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve Stripe session details
            session = stripe.checkout.Session.retrieve(session_id)

            # Attempt to find the order associated with this session
            order = Order.objects.filter(payment_token=session_id).first()
            order.payment_status = 'paid'
            order.ordered = True
            order.date_ordered = datetime.now()
            order.save()

            if not order:
                return Response({'error': 'Order not found for the given session ID.'}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({'error': f'Stripe error: {e.user_message}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def convert_querydict_to_dict(querydict):
    # Convert the QueryDict to a dictionary
    result = {}
    for key, value in querydict.lists():
        # If there's only one item in the value list, unpack it
        if len(value) == 1:
            result[key] = value[0]
        else:
            result[key] = value
    
    # Handle specific conversions
    # Convert address and tags if they are serialized as JSON strings
    if 'address' in result and isinstance(result['address'], list):
        # Convert address string to a dictionary if nested
        result['address'] = {
            'street_address': result['address'][0].get('street_address', [])[0],
            'city': result['address'][0].get('city', [])[0],
            'state': result['address'][0].get('state', [])[0],
            'zip_code': result['address'][0].get('zip_code', [])[0],
            'country': result['address'][0].get('country', [])[0]
        }

    if 'tags' in result:
        try:
            # Parse the tags JSON string to a Python list
            result['tags'] = eval(result['tags'])
        except Exception as e:
            print("Error converting tags:", e)

    return result

class CategoryViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]  # Custom authentication for JWT from cookies

    def list(self, request):
        # List all categories
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAdminUser]  # Only admin users can create categories
        self.check_permissions(request)  # Ensure permission check is applied

        # Create a new category
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the category to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAdminUser]  # Only admin users can retrieve categories
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Retrieve a category by primary key (pk)
        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAdminUser]  # Only admin users can update categories
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Update a category by primary key (pk)
        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated category to the database
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAdminUser]  # Only admin users can delete categories
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Delete a category by primary key (pk)
        category = Category.objects.get(pk=pk)
        category.delete()  # Delete the category from the database
        return Response(status=status.HTTP_204_NO_CONTENT)

class RootCategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer  # Use CategorySerializer to serialize category data

    def get_queryset(self):
        # Only return categories that are root (parent is null)
        return Category.objects.filter(parent__isnull=True)

class TagViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]  # Custom JWT authentication for tags

    def list(self, request):
        self.permission_classes = [permissions.IsAdminUser]  # Only admin users can list tags
        self.check_permissions(request)  # Ensure permission check is applied
        
        # List all tags
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAuthenticated]  # Any authenticated user can create tags
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Create a new tag
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the tag to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]  # Any authenticated user can retrieve tags
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Retrieve a tag by primary key (pk)
        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]  # Any authenticated user can update tags
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Update a tag by primary key (pk)
        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated tag to the database
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]  # Any authenticated user can delete tags
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Delete a tag by primary key (pk)
        tag = Tag.objects.get(pk=pk)
        tag.delete()  # Delete the tag from the database
        return Response(status=status.HTTP_204_NO_CONTENT)

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()  # Define the default queryset for equipment
    serializer_class = EquipmentSerializer  # Define the serializer for equipment data

    authentication_classes = [JWTAuthenticationFromCookie]  # Use custom JWT authentication for equipment

    def list(self, request):
        # List all equipment
        queryset = Equipment.objects.all()
        serializer = EquipmentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            # Get images if sent with the 'images' key
            images = request.FILES.getlist('images')
            print("Images received:", images)

            # Convert incoming querydict to a structured dictionary
            data = convert_querydict_to_dict(request.data)
            print("Converted form data:", data)

            # Group address-related fields together in a dictionary
            address = {
                'street_address': data.pop('street_address', None),
                'city': data.pop('city', None),
                'state': data.pop('state', None),
                'zip_code': data.pop('zip_code', None),
                'country': data.pop('country', None)
            }
            data['address'] = address
            print("Address data:", address)

            # Convert tags to a list of dictionaries
            if 'tags' in data:
                data['tags'] = [{'name': tag} for tag in data.pop('tags')]
            print("Tags data:", data.get('tags', []))

            # Convert specifications from string to a list of dictionaries
            if 'specifications' in data:
                data['specifications'] = json.loads(data.pop('specifications'))
            print("Specifications data:", data.get('specifications', []))

            specifications_data = data['specifications']

            # Initialize and validate the equipment serializer
            print("Initializing equipment serializer with data:", data)
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)

            # Save the equipment instance to generate the ID
            equipment = serializer.save()
            print("Equipment instance saved:", equipment)

            # Now create the specifications associated with the equipment
            for spec in specifications_data:
                print("Processing specification:", spec)

                # Rename 'key' to 'name' in the specification data
                if 'key' in spec:
                    spec['name'] = spec.pop('key', None)
                    print(f"Renamed specification: {spec}")

                # Ensure 'name' is present
                if not spec.get('name'):
                    print("Specification 'name' is missing")
                    return Response({'detail': 'Specification name is required.'}, status=status.HTTP_400_BAD_REQUEST)

                # Serialize and save the specification
                specification_serializer = SpecificationSerializer(data=spec, context={'equipment': equipment})
                print("Spec data for specification serializer:", spec)
                if specification_serializer.is_valid():
                    specification_serializer.save(equipment=equipment)
                    print(f"Specification saved: {specification_serializer.data}")
                else:
                    print("Specification serializer errors:", specification_serializer.errors)
                    return Response(specification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Handle images if necessary
            if images:
                print(f"Processing {len(images)} images.")
                for image in images:
                    # Save images for the equipment
                    equipment.images.create(image=image)
                    print(f"Image saved: {image}")

            # Return the response with the created equipment data
            headers = self.get_success_headers(serializer.data)
            print("Returning response data:", serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            print("Error during data processing:", e)
            return Response({'detail': 'An error occurred while processing the data.'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        # Retrieve equipment by primary key (pk)
        equipment = Equipment.objects.get(pk=pk)
        equipment_reviews = equipment.equipment_reviews.filter(review_text__isnull=False).exclude(review_text="")
        serializer = EquipmentSerializer(equipment)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can update equipment
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Update equipment by primary key (pk)
        equipment = Equipment.objects.get(pk=pk)
        serializer = EquipmentSerializer(equipment, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated equipment to the database
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can delete equipment
        self.check_permissions(request)  # Ensure permission check is applied
        
        # Delete equipment by primary key (pk)
        equipment = Equipment.objects.get(pk=pk)
        equipment.delete()  # Delete the equipment from the database
        return Response(status=status.HTTP_204_NO_CONTENT)
class ImageViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication for image endpoints

    def list(self, request):
        # Only admin users can list all images
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Image.objects.all()  # Get all image objects
        serializer = ImageSerializer(queryset, many=True)  # Serialize the images
        return Response(serializer.data)  # Return the serialized image data

    def create(self, request):
        # Uncomment below lines if authentication is needed for creating images
        # self.permission_classes = [permissions.IsAuthenticated]
        # self.check_permissions(request)  # Ensure permission check is applied
        
        serializer = ImageSerializer(data=request.data)  # Deserialize image data
        if serializer.is_valid():
            serializer.save()  # Save the image to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the serialized data with 201 status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if invalid

    def retrieve(self, request, pk=None):
        # Only authenticated users can retrieve individual images
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)  # Get image by primary key
        serializer = ImageSerializer(image)  # Serialize the image
        return Response(serializer.data)  # Return the serialized data

    def update(self, request, pk=None):
        # Only authenticated users can update images
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)  # Get image by primary key
        serializer = ImageSerializer(image, data=request.data)  # Deserialize and validate updated data
        if serializer.is_valid():
            serializer.save()  # Save the updated image
            return Response(serializer.data)  # Return updated data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if invalid

    def destroy(self, request, pk=None):
        # Only authenticated users can delete images
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)  # Get image by primary key
        image.delete()  # Delete the image from the database
        return Response(status=status.HTTP_204_NO_CONTENT)  # Return 204 status for successful deletion


class SpecificationViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication for specification endpoints

    def list(self, request):
        # Only admin users can list all specifications
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Specification.objects.all()  # Get all specification objects
        serializer = SpecificationSerializer(queryset, many=True)  # Serialize the specifications
        return Response(serializer.data)  # Return the serialized data

    def create(self, request):
        # Only authenticated users can create specifications
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        
        serializer = SpecificationSerializer(data=request.data)  # Deserialize specification data
        if serializer.is_valid():
            serializer.save()  # Save the specification to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return created data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if invalid

    def retrieve(self, request, pk=None):
        # Only authenticated users can retrieve individual specifications
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)  # Get specification by primary key
        serializer = SpecificationSerializer(specification)  # Serialize the specification
        return Response(serializer.data)  # Return the serialized data

    def update(self, request, pk=None):
        # Only authenticated users can update specifications
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)  # Get specification by primary key
        serializer = SpecificationSerializer(specification, data=request.data)  # Deserialize and validate updated data
        if serializer.is_valid():
            serializer.save()  # Save the updated specification
            return Response(serializer.data)  # Return updated data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if invalid

    def destroy(self, request, pk=None):
        # Only authenticated users can delete specifications
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)  # Get specification by primary key
        specification.delete()  # Delete the specification from the database
        return Response(status=status.HTTP_204_NO_CONTENT)  # Return 204 status for successful deletion


class ReviewViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]  # Use JWT authentication from cookies
    serializer_class = ReviewSerializer  # Define the serializer for reviews
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can perform review actions

    def list(self, request):
        # Filter reviews to include only those with non-null, non-empty review_text
        queryset = Review.objects.filter(review_text__isnull=False).exclude(review_text="")
        
        serializer = ReviewSerializer(queryset, many=True)  # Serialize the reviews
        return Response(serializer.data)  # Return the serialized review data

    def create(self, request):
        # Add the user to the request data before validation
        data = request.data.copy()  # Make a copy of the request data
        data['user'] = request.user.id  # Add the user ID to the review data

        serializer = ReviewSerializer(data=data)  # Deserialize review data
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save the review with the user information
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return created review data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if invalid

    def retrieve(self, request, pk=None):
        # Only authenticated users can retrieve individual reviews
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        review = Review.objects.get(pk=pk)  # Get review by primary key
        serializer = ReviewSerializer(review)  # Serialize the review
        return Response(serializer.data)  # Return the serialized review data

    def update(self, request, pk=None):
        # Only authenticated users can update reviews
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        review = Review.objects.get(pk=pk)  # Get review by primary key
        serializer = ReviewSerializer(review, data=request.data)  # Deserialize and validate updated data
        if serializer.is_valid():
            serializer.save()  # Save the updated review
            return Response(serializer.data)  # Return updated review data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return errors if invalid

    def destroy(self, request, pk=None):
        # Only authenticated users can delete reviews
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        review = Review.objects.get(pk=pk)  # Get review by primary key
        review.delete()  # Delete the review from the database
        return Response(status=status.HTTP_204_NO_CONTENT)  # Return 204 status for successful deletion
class CartViewSet(viewsets.ModelViewSet):
    # Authentication using JWT token from cookies
    authentication_classes = [JWTAuthenticationFromCookie]
    # Serializer to handle Cart data serialization/deserialization
    serializer_class = CartSerializer
    # Permission ensures only authenticated users can access the cart
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure a cart exists for the user before returning the queryset
        Cart.objects.get_or_create(user=self.request.user)
        # Return the cart for the current user
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Try to get or create a cart for the user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        
        if not created:
            # If the cart already exists, return details of the existing cart
            serializer = self.get_serializer(cart)
            return Response(
                {"detail": "A cart already exists for this user.", "cart": serializer.data},
                status=status.HTTP_200_OK
            )

        # If a new cart was created, return its details
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Get the cart object to update
        cart = self.get_object()
        # Validate the data and save changes to the cart
        serializer = self.get_serializer(cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Get the cart object to delete
        cart = self.get_object()
        # Delete the cart
        cart.delete()
        return Response({"detail": "Cart deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class CartItemViewSet(viewsets.ModelViewSet):
    # Authentication using JWT token from cookies
    authentication_classes = [JWTAuthenticationFromCookie]
    # Serializer to handle CartItem data serialization/deserialization
    serializer_class = CartItemSerializer
    # Permission ensures only authenticated users can access cart items
    permission_classes = [permissions.IsAuthenticated]

    def get_cart_item(self):
        # Get or create a cart for the user
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        # Get a specific cart item by its ID provided in the request data
        return CartItem.objects.get(id=self.request.data.get('id'))

    def get_queryset(self):
        # Ensure a cart exists for the user, then filter cart items by that cart
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=user_cart)

    def create(self, request, *args, **kwargs):
        # Get or create a cart for the user
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        
        # Extract item data from the request
        item_data = request.data
        item_id = item_data.get("item")  # Get the item ID
        item_quantity = item_data.get("quantity", 1)  # Default quantity is 1
        
        # Check if the item already exists in the user's cart
        existing_cart_item = CartItem.objects.filter(cart=user_cart, item_id=item_id).first()

        if existing_cart_item:
            # Normalize start and end dates to compare only the date portion (ignores time)
            new_start_date = datetime.strptime(item_data.get("start_date"), "%Y-%m-%d").date()
            new_end_date = datetime.strptime(item_data.get("end_date"), "%Y-%m-%d").date()

            existing_start_date = existing_cart_item.start_date  # Already a date object
            existing_end_date = existing_cart_item.end_date  # Already a date object

            if (existing_start_date != new_start_date or existing_end_date != new_end_date):
                # If dates differ, reset the quantity and update the dates
                existing_cart_item.quantity = item_quantity
                existing_cart_item.start_date = new_start_date
                existing_cart_item.end_date = new_end_date
            else:
                # If dates are the same, just increase the quantity
                existing_cart_item.quantity += item_quantity

            # Save the updated cart item
            existing_cart_item.save()
            serializer = self.get_serializer(existing_cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # If the item does not exist in the cart, create a new cart item
        item_data['cart'] = user_cart.id  # Associate the item with the user's cart
        serializer = self.get_serializer(data=item_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Retrieve the cart item to be updated
        cart_item = self.get_cart_item()
        # Update the cart item with the provided data
        serializer = self.get_serializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Delete a specific cart item
        cart_item = self.get_object()
        cart_item.delete()
        return Response({"detail": "Cart item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class OrderActionView(APIView):
    # Authentication using JWT token from cookies
    authentication_classes = [JWTAuthenticationFromCookie]

    def post(self, request, pk, action):
        try:
            # Get the order by its ID for the current user
            order = Order.objects.get(id=pk, user=request.user)

            if action == 'terminate':
                # Handle terminating the rental
                order.terminate_rental()
            elif action == 'delete':
                # Handle deleting the order
                order.delete()
            elif action == 'reorder':
                # Handle reordering the same items
                new_order = order.reorder()
                return Response({'message': 'Order reordered successfully', 'new_order_id': new_order.id}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': f'Order {action} action successful'}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            # If order is not found for the current user, return an error
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            # Handle potential errors such as invalid data
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderViewSet(viewsets.ViewSet):
    # Authentication using JWT token from cookies
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        # List all orders for the current user
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Create a new order for the user
        self.check_permissions(request)

        data = request.data
        data['user'] = request.user.id

        try:
            # Fetch the user's cart
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "No cart found for the user"}, status=status.HTTP_404_NOT_FOUND)

        # Get cart items
        cart_items = cart.cart_items.all()

        if not cart_items.exists():
            return Response({"error": "Cart is empty, cannot create an order"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price and items
        order_total_price = sum(item.quantity * item.item.hourly_rate for item in cart_items)
        total_order_items = sum(item.quantity for item in cart_items)

        data['order_total_price'] = order_total_price
        data['total_order_items'] = total_order_items

        # Serialize and save the order
        order_serializer = OrderSerializer(data=data)
        if order_serializer.is_valid():
            # Save the order and create associated order items
            order = order_serializer.save(user=request.user)

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    start_date=cart_item.start_date,
                    end_date=cart_item.end_date
                )

            # Clear the cart after creating the order
            cart_items.delete()

            # Stripe payment integration
            try:
                # Convert the total price to cents for Stripe
                amount_in_cents = int(order_total_price * 100)

                # Create a PaymentIntent for Stripe payment processing
                intent = stripe.PaymentIntent.create(
                    amount=amount_in_cents,
                    currency='usd',
                    automatic_payment_methods={'enabled': True},
                )

                # Update the order with the payment token
                order.payment_token = intent.id
                order.payment_status = 'pending'
                order.save()

                # Return the client secret for the frontend to process the payment
                return Response({
                    'clientSecret': intent.client_secret,
                    'order_id': order.id,
                }, status=status.HTTP_201_CREATED)

            except stripe.error.StripeError as e:
                # Handle payment processing errors
                return Response({"error": f"Payment processing failed: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, pk=None):
        # Retrieve a specific order by its ID
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # Update an existing order
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        order = Order.objects.get(pk=pk, user=request.user)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # Delete an order
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        order = Order.objects.get(pk=pk, user=request.user)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderItemViewSet(viewsets.ViewSet):
    # JWT authentication to ensure that users are authenticated via cookies
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        # Ensure the user is authenticated before accessing the list of order items
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Permission check

        # Retrieve all order items from the database
        queryset = OrderItem.objects.all()
        # Serialize the data and return it in the response
        serializer = OrderItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Ensure the user is authenticated before creating a new order item
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Permission check

        # Serialize the incoming data to create a new order item
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            # If the data is valid, save the new order item and return a success response
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # If the data is invalid, return an error response with the validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        # Ensure the user is authenticated before retrieving a specific order item
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Permission check

        # Retrieve a specific order item based on the provided ID (pk) and user
        order_item = OrderItem.objects.get(pk=pk, user=request.user)
        # Serialize the retrieved order item and return it in the response
        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # Ensure the user is authenticated before updating an existing order item
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Permission check

        # Retrieve the order item to be updated based on the provided ID (pk)
        order_item = OrderItem.objects.get(pk=pk)
        # Serialize the incoming data and update the order item
        serializer = OrderItemSerializer(order_item, data=request.data)
        if serializer.is_valid():
            # If the data is valid, save the updated order item and return a success response
            serializer.save()
            return Response(serializer.data)
        # If the data is invalid, return an error response with the validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # Ensure the user is authenticated before deleting an order item
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Permission check

        # Retrieve and delete the specified order item based on the provided ID (pk)
        order_item = OrderItem.objects.get(pk=pk)
        order_item.delete()
        # Return a success response indicating that the order item has been deleted
        return Response(status=status.HTTP_204_NO_CONTENT)
