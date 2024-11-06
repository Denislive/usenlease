# rentals/views.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.utils.translation import gettext_lazy as _
import json

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



from django.http import QueryDict

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
    authentication_classes = [JWTAuthentication]

    def list(self, request):
         # Ensure permission check is applied
        queryset = Category.objects.filter(parent=None)
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

    authentication_classes = [JWTAuthentication]

    def list(self, request):
        queryset = Equipment.objects.all()
        serializer = EquipmentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:    
            images = request.FILES.getlist('images')  # Assumes images are sent with the 'images' key
            print()
            print('Images',images)
            # Convert incoming data to a structured dictionary
            data = convert_querydict_to_dict(request.data)
            print("Structured data before adjustments:", data['images'])

            
            # Ensure address fields are grouped in a dictionary for the `address` field
            data['address'] = {
                'street_address': data.pop('street_address', None),
                'city': data.pop('city', None),
                'state': data.pop('state', None),
                'zip_code': data.pop('zip_code', None),
                'country': data.pop('country', None)
            }

            # Convert tags to the expected format (list of dictionaries)
            if 'tags' in data:
                # Assuming tags are meant to be strings, convert to dicts if necessary
                data['tags'] = [{'name': tag} for tag in data.pop('tags')]

            print("Structured data with nested address and formatted tags:", data)
        except Exception as e:
            print("Error structuring data:", e)
            raise

        # Initialize serializer with structured data
        try:
            serializer = self.get_serializer(data=data, context={'request': request})
            print("Serializer initialized successfully with data.")
        except Exception as e:
            print("Error initializing serializer:", e)
            raise

        # Validate serializer data
        try:
            serializer.is_valid(raise_exception=True)
            print("Data is valid.")
        except Exception as e:
            print("Error validating serializer data:", e)
            print("Validation errors:", serializer.errors)
            raise

        # Save the validated data and return the response
        try:
            equipment = serializer.save(request=request)
            print("Equipment instance created successfully:", equipment)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print("Error saving equipment instance or preparing response:", e)
            raise





    def retrieve(self, request, pk=None):
    
        equipment = Equipment.objects.get(pk=pk)
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
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        queryset = Review.objects.all()
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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


class CartViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        try:
            # Get the cart for the authenticated user
            cart = Cart.objects.get(user=request.user)
            
            # Get all cart items related to the cart
            cart_items = CartItem.objects.filter(cart=cart)  # Corrected here
            
            # Serialize the cart data, including related cart items
            serializer = CartSerializer(cart)
            # Add cart_items to the serialized data
            cart_data = serializer.data
            cart_data['cart_items'] = CartItemSerializer(cart_items, many=True).data  # Ensure you have a CartItemSerializer
            
            return Response(cart_data)
        
        except Cart.DoesNotExist:
            return Response([], status=status.HTTP_204_NO_CONTENT)


    def create(self, request):
        # Ensure the user is authenticated
        self.check_permissions(request)

        # Retrieve or create a Cart for the authenticated user
        cart, created = Cart.objects.get_or_create(user=request.user)

        # If cart items are provided in the request, update them
        cart_items_data = request.data.get("cart_items", [])
        print("cart items data", cart_items_data)
        
        for item_data in cart_items_data:
            # Ensure each cart item belongs to the current cart and is added/updated properly
            cart_item, created = CartItem.objects.update_or_create(
                cart=cart,
                defaults={
                    'quantity': item_data.get("quantity"),
                    'start_date': item_data.get("start_date"),
                    'end_date': item_data.get("end_date"),
                    'total': item_data.get("total"),
                }
            )
        
        # Serialize and return the updated cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        try:
            cart = Cart.objects.get(pk=pk, user=request.user)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        try:
            cart = Cart.objects.get(pk=pk, user=request.user)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class CartItemViewSet(viewsets.ViewSet):

    authentication_classes = [JWTAuthentication]

    def list(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = CartItem.objects.all()
        serializer = CartItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        try:
            cart_item = CartItem.objects.get(pk=pk)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        try:
            cart_item = CartItem.objects.get(pk=pk)
            serializer = CartItemSerializer(cart_item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        try:
            cart_item = CartItem.objects.get(pk=pk)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        self.check_permissions(request)  # Ensure permission check is applied
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the order with the current user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    authentication_classes = [JWTAuthentication]

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