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
            user = request.user
            cart = Cart.objects.get(user=user)

            if not cart.cart_items.exists():
                return Response({"error": "Cart is empty, cannot create a session."}, status=status.HTTP_400_BAD_REQUEST)

            # Prepare order data
            cart_items = cart.cart_items.all()
            order_total_price = cart.get_cart_total
            total_order_items = cart.get_cart_items

            # Create the order
            order_serializer = OrderSerializer(data={
                'user': user.id,
                'order_total_price': order_total_price,
                'total_order_items': total_order_items,
            })
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save()

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    start_date=cart_item.start_date,
                    end_date=cart_item.end_date,
                )

            # Convert price to cents
            amount_in_cents = int(order_total_price * 100)

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
        session_id = request.query_params.get('session_id')

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
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
         # Ensure permission check is applied
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        category = Category.objects.get(pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

class RootCategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True)


class TagViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Tag.objects.all()
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        tag = Tag.objects.get(pk=pk)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        tag = Tag.objects.get(pk=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        # queryset = Equipment.objects.filter(owner=request.user.id)
        queryset = Equipment.objects.all()
        serializer = EquipmentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            # Get images if sent with the 'images' key
            images = request.FILES.getlist('images')  # Assumes images are sent with the 'images' key
            print("Images received:", images)

            # Convert incoming querydict to a structured dictionary
            data = convert_querydict_to_dict(request.data)
            print("Converted form data:", data)

            # Ensure address fields are grouped in a dictionary for the `address` field
            address = {
                'street_address': data.pop('street_address', None),
                'city': data.pop('city', None),
                'state': data.pop('state', None),
                'zip_code': data.pop('zip_code', None),
                'country': data.pop('country', None)
            }
            data['address'] = address
            print("Address data:", address)

            # Convert tags to a list of dictionaries for `tags`
            if 'tags' in data:
                data['tags'] = [{'name': tag} for tag in data.pop('tags')]
            print("Tags data:", data.get('tags', []))

            # Convert specifications from string to list of dictionaries
            if 'specifications' in data:
                data['specifications'] = json.loads(data.pop('specifications'))
            print("Specifications data:", data.get('specifications', []))

            specifications_data = data['specifications']

            # Initialize and validate the equipment serializer
            print("Initializing equipment serializer with data:", data)
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)

            # Save the equipment instance first to generate the ID
            equipment = serializer.save()
            print("Equipment instance saved:", equipment)

            # Now create the specifications associated with the equipment
            for spec in specifications_data:
                print("Processing specification:", spec)
                
                # Rename 'key' to 'name' in the specification data
                if 'key' in spec:
                    spec['name'] = spec.pop('key', None)  # Rename 'key' to 'name'
                    print(f"Renamed specification: {spec}")
                
                # Ensure 'name' is now present
                if not spec.get('name'):
                    print("Specification 'name' is missing")
                    return Response({'detail': 'Specification name is required.'}, status=status.HTTP_400_BAD_REQUEST)

                # Ensure we include the equipment instance in the context for the Specification serializer
                specification_serializer = SpecificationSerializer(data=spec, context={'equipment': equipment})
                print("Spec data for specification serializer:", spec)
                if specification_serializer.is_valid():
                    specification_serializer.save(equipment=equipment)  # Create the specification instance
                    print(f"Specification saved: {specification_serializer.data}")
                else:
                    print("Specification serializer errors:", specification_serializer.errors)
                    return Response(specification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Handle images if necessary
            if images:
                print(f"Processing {len(images)} images.")
                for image in images:
                    # Example of saving images (if your Equipment model supports this)
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
    
        equipment = Equipment.objects.get(pk=pk)
        equipment_reviews = equipment.equipment_reviews.filter(review_text__isnull=False).exclude(review_text="")
        serializer = EquipmentSerializer(equipment)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        equipment = Equipment.objects.get(pk=pk)
        serializer = EquipmentSerializer(equipment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        equipment = Equipment.objects.get(pk=pk)
        equipment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Image.objects.all()
        serializer = ImageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        # self.permission_classes = [permissions.IsAuthenticated]
        # self.check_permissions(request)  # Ensure permission check is applied
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)
        serializer = ImageSerializer(image)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)
        serializer = ImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        image = Image.objects.get(pk=pk)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SpecificationViewSet(viewsets.ViewSet):

    authentication_classes = [JWTAuthentication]

    def list(self, request):
        self.permission_classes = [permissions.IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Specification.objects.all()
        serializer = SpecificationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        serializer = SpecificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)
        serializer = SpecificationSerializer(specification)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)
        serializer = SpecificationSerializer(specification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        specification = Specification.objects.get(pk=pk)
        specification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Filter reviews to include only those with non-null, non-empty review_text
        queryset = Review.objects.filter(review_text__isnull=False).exclude(review_text="")
        
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Add the user to the request data before validation
        data = request.data.copy()
        data['user'] = request.user.id  # or request.user.pk, depending on your setup

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # pass the user to the save method
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        review = Review.objects.get(pk=pk)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        review = Review.objects.get(pk=pk)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        review = Review.objects.get(pk=pk)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure a cart exists for the user before returning the queryset
        Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(user=self.request.user)

    

    def create(self, request, *args, **kwargs):
        # Get or create a cart for the user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        
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

    def update(self, request, *args, **kwargs):
        # Ensure a cart exists for the user before updating
        cart = self.get_object()
        serializer = self.get_serializer(cart, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Ensure a cart exists before attempting to delete it
        cart = self.get_object()
        cart.delete()
        return Response({"detail": "Cart deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class CartItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_cart_item(self):
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.get(id=self.request.data.get('id'))

    def get_queryset(self):
        # Ensure a cart exists for the user and filter cart items by the user's cart
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=user_cart)

    def create(self, request, *args, **kwargs):
        # Ensure a cart exists for the user
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user)
        
        # Extract data for the item to be added/updated
        item_data = request.data
        item_id = item_data.get("item")  # Get the item ID
        item_quantity = item_data.get("quantity", 1)
        
        # Check if the item already exists in the user's cart
        existing_cart_item = CartItem.objects.filter(cart=user_cart, item_id=item_id).first()

        if existing_cart_item:
            # Normalize the start_date and end_date to only compare the date (ignore time)
            new_start_date = datetime.strptime(item_data.get("start_date"), "%Y-%m-%d").date()
            new_end_date = datetime.strptime(item_data.get("end_date"), "%Y-%m-%d").date()

            existing_start_date = existing_cart_item.start_date  # No need for .date(), it's already a date
            existing_end_date = existing_cart_item.end_date  # No need for .date(), it's already a date

            if (existing_start_date != new_start_date or existing_end_date != new_end_date):
                # If the dates are different, reset the quantity and update dates
                existing_cart_item.quantity = item_quantity  # Set the quantity to the new value
                existing_cart_item.start_date = new_start_date
                existing_cart_item.end_date = new_end_date
            else:
                # If the dates are the same, increment the quantity
                existing_cart_item.quantity += item_quantity

            existing_cart_item.save()
            serializer = self.get_serializer(existing_cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # If the item does not exist in the cart, create a new cart item
        item_data['cart'] = user_cart.id  # Associate the new cart item with the user's cart
        serializer = self.get_serializer(data=item_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        
    def update(self, request, *args, **kwargs):
        # item_id = request.data.get('id') 
        # cart_item = CartItem.objects.get(id=item_id)
        cart_item = self.get_cart_item()
        serializer = self.get_serializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart_item.delete()
        return Response({"detail": "Cart item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# class CartViewSet(viewsets.ViewSet):
#     authentication_classes = [JWTAuthenticationFromCookie]
#     serializer_class = CartSerializer
#     def get_queryset(self):
#         # Only return the cart for the authenticated user
#         return Cart.objects.filter(user=self.request.user)

#     def list(self, request):
#         try:
#             # Get the cart for the authenticated user
#             cart = Cart.objects.get(user=request.user)
            
#             # Get all cart items related to the cart
#             cart_items = CartItem.objects.filter(cart=cart)  # Corrected here
            
#             # Serialize the cart data, including related cart items
#             serializer = CartSerializer(cart)
#             # Add cart_items to the serialized data
#             cart_data = serializer.data
#             cart_data['cart_items'] = CartItemSerializer(cart_items, many=True).data  # Ensure you have a CartItemSerializer
            
#             return Response(cart_data)
        
#         except Cart.DoesNotExist:
#             return Response([], status=status.HTTP_204_NO_CONTENT)

#     def create(self, request):
#         # Print incoming request data for debugging purposes
#         print()
#         print("Creatiioon request data", request.data)

#         # Ensure the user is authenticated
#         self.check_permissions(request)

#         # Ensure request data is a list of cart items
#         if not isinstance(request.data.get('cart_items'), list):
#             return Response({"detail": "Invalid data format. Expected a list of cart items."}, status=status.HTTP_400_BAD_REQUEST)

#         cart_data = request.data.get('cart_items')
#         if not cart_data:
#             return Response({"detail": "Cart items are required."}, status=status.HTTP_400_BAD_REQUEST)
#         print()

#         print("Cart data received:", cart_data)

#         # Retrieve or create a Cart for the authenticated user
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Process each cart item
#         for item_data in cart_data:
#             item_response = self.process_cart_item(item_data, cart)
#             if item_response:
#                 return item_response

#         # Serialize and return the updated cart
#         cart_serializer = CartSerializer(cart)
#         return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

#     def process_cart_item(self, item_data, cart):
#         # Extract item details

#         equipment_id = item_data.get('item')
#         quantity = item_data.get("quantity")
#         start_date = item_data.get("start_date")
#         end_date = item_data.get("end_date")

#         if not equipment_id or not start_date or not end_date:
#             return Response({"detail": "Missing required fields for an item."}, status=status.HTTP_400_BAD_REQUEST)

#         print(f"Processing item: Equipment ID: {equipment_id}, Quantity: {quantity}, Start Date: {start_date}, End Date: {end_date}")

#         try:
#             equipment = Equipment.objects.get(id=equipment_id)
#         except Equipment.DoesNotExist:
#             return Response({"detail": f"Equipment with ID {equipment_id} not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Create a new cart item (no updates)
#         CartItem.objects.create(
#             cart=cart,
#             item=equipment,
#             quantity=quantity,
#             start_date=start_date,
#             end_date=end_date
#         )

#         return None


    

#     def update(self, request, pk=None):
#         # Print incoming request data for debugging purposes
#         print()
#         print("update requst data", request.data)
        

#         # If request data is a list of cart items, directly use it
#         if isinstance(request.data, list):
#             cart_data = request.data
#         else:
#             return Response({"detail": "Invalid data format. Expected a list of cart items."}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Ensure cart_data is not empty
#         if not cart_data:
#             return Response({"detail": "Cart items are required."}, status=status.HTTP_400_BAD_REQUEST)
#         print()

#         print("Cart data received for update:", cart_data)

#         # Retrieve the cart for the authenticated user
#         cart = get_object_or_404(Cart, user=request.user)

#         # Iterate over the cart items data
#         for item_data in cart_data:
#             equipment_id = item_data.get('item', {}).get('id')
#             quantity = item_data.get("quantity")
#             start_date = item_data.get("start_date")
#             end_date = item_data.get("end_date")
            
#             if not equipment_id or not start_date or not end_date:
#                 return Response({"detail": "Missing required fields for an item."}, status=status.HTTP_400_BAD_REQUEST)

#             print(f"Equipment ID: {equipment_id}, Quantity: {quantity}, Start Date: {start_date}, End Date: {end_date}")
            
#             # Find the Equipment instance or return 404 if not found
#             equipment = get_object_or_404(Equipment, id=equipment_id)
            
#             # Find the existing cart item
#             cart_item = CartItem.objects.filter(cart=cart, item=equipment).first()

#             if cart_item:
#                 # If the item exists, update its quantity and dates
#                 cart_item.quantity = quantity  # Update the quantity
#                 cart_item.start_date = start_date  # Update the start date
#                 cart_item.end_date = end_date  # Update the end date
#                 cart_item.save()  # Save updated cart item
#             else:
#                 # If the item doesn't exist, create a new cart item
#                 CartItem.objects.create(
#                     cart=cart,
#                     item=equipment,
#                     quantity=quantity,
#                     start_date=start_date,
#                     end_date=end_date
#                 )

#         # Serialize and return the updated cart
#         cart_serializer = CartSerializer(cart)
#         return Response(cart_serializer.data, status=status.HTTP_200_OK)

#     def retrieve(self, request, pk=None):
#         self.permission_classes = [permissions.IsAuthenticated]
#         self.check_permissions(request)  # Ensure permission check is applied
#         try:
#             cart = Cart.objects.get(pk=pk, user=request.user)
#             serializer = CartSerializer(cart)
#             return Response(serializer.data)
#         except Cart.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#     def destroy(self, request, pk=None):
#         self.permission_classes = [permissions.IsAuthenticated]
#         self.check_permissions(request)  # Ensure permission check is applied
#         try:
#             cart = Cart.objects.get(pk=pk, user=request.user)
#             cart.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Cart.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
        
# class CartItemViewSet(viewsets.ViewSet):

#     authentication_classes = [JWTAuthentication]

#     def list(self, request):
#         self.permission_classes = [permissions.IsAuthenticated]
#         self.check_permissions(request)  # Ensure permission check is applied
#         queryset = CartItem.objects.all()
#         serializer = CartItemSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def create(self, request):
#         self.permission_classes = [permissions.IsAuthenticated]
#         self.check_permissions(request)  # Ensure permission check is applied
#         serializer = CartItemSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def retrieve(self, request, pk=None):
#         self.permission_classes = [permissions.IsAuthenticated]
#         self.check_permissions(request)  # Ensure permission check is applied
#         try:
#             cart_item = CartItem.objects.get(pk=pk)
#             serializer = CartItemSerializer(cart_item)
#             return Response(serializer.data)
#         except CartItem.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#     def update(self, request, pk=None):
#         self.permission_classes = [permissions.IsAuthenticated]
#         self.check_permissions(request)  # Ensure permission check is applied
#         try:
#             cart_item = CartItem.objects.get(pk=pk)
#             serializer = CartItemSerializer(cart_item, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except CartItem.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#     def destroy(self, request, pk=None):
#         self.permission_classes = [permissions.IsAuthenticated]
#         self.check_permissions(request)  # Ensure permission check is applied
#         try:
#             cart_item = CartItem.objects.get(pk=pk)
#             cart_item.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except CartItem.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)


class OrderActionView(APIView):
    authentication_classes = [JWTAuthenticationFromCookie]


    def post(self, request, pk, action):
        print("data", request.data)
        try:
            order = Order.objects.get(id=pk, user=request.user)

            if action == 'terminate':
                order.terminate_rental()
            elif action == 'delete':
                order.delete()
            elif action == 'reorder':
                new_order = order.reorder()
                return Response({'message': 'Order reordered successfully', 'new_order_id': new_order.id}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': f'Order {action} action successful'}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class OrderViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
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

        # Calculate order total price and total order items
        order_total_price = sum(item.quantity * item.item.hourly_rate for item in cart_items)
        total_order_items = sum(item.quantity for item in cart_items)

        data['order_total_price'] = order_total_price
        data['total_order_items'] = total_order_items

        # Serialize and save the order
        order_serializer = OrderSerializer(data=data)
        if order_serializer.is_valid():
            # Save the order and create order items
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

            # Payment logic (Stripe integration)
            try:
                # Convert the total price to cents (Stripe requires amount in cents)
                amount_in_cents = int(order_total_price * 100)

                # Create a PaymentIntent with Stripe
                intent = stripe.PaymentIntent.create(
                    amount=amount_in_cents,
                    currency='usd',
                    automatic_payment_methods={'enabled': True},
                )

                # Update the order with the payment token
                order.payment_token = intent.id
                order.payment_status = 'pending'  # Initially set to pending before payment confirmation
                order.save()

                # Return the client secret for the frontend to process the payment
                return Response({
                    'clientSecret': intent.client_secret,
                    'order_id': order.id,
                }, status=status.HTTP_201_CREATED)

            except stripe.error.StripeError as e:
                return Response({"error": f"Payment processing failed: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        order = Order.objects.get(pk=pk, user=request.user)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        order = Order.objects.get(pk=pk, user=request.user)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderItemViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = OrderItem.objects.all()
        serializer = OrderItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        order_item = OrderItem.objects.get(pk=pk, user=request.user)
        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        order_item = OrderItem.objects.get(pk=pk)
        serializer = OrderItemSerializer(order_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        order_item = OrderItem.objects.get(pk=pk)
        order_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)