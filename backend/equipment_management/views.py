# rentals/views.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
import json
from datetime import datetime
from rest_framework import generics


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