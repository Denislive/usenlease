# rentals/views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password

from rest_framework import viewsets
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import IntegrityError


from .models import User, Address, PhysicalAddress, CreditCard
from .serializers import UserSerializer, AddressSerializer, PhysicalAddressSerializer, CreditCardSerializer

# views.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView


from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import UserSerializer


from django.utils import timezone
from datetime import timedelta, datetime
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.exceptions import TokenError



class LoginView(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            
            # Serialize the user details
            user_data = UserSerializer(user).data

            response_data = {
                "user": user_data,  # Include all user details here
            }
            response = Response(response_data, status=status.HTTP_200_OK)

            # Set the access token in an HTTP-only cookie
            response.set_cookie(
                key="access_token", 
                value=str(refresh.access_token),
                httponly=True,
                secure=False,  # Set to True if using HTTPS
                samesite='None',
                path="/"
            )

            # Set the refresh token as well
            response.set_cookie(
                key="refresh", 
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite='None',
                path="/"
            )

            # Print tokens directly for verification
            print("Tokens before setting cookies:")
            print(f"Access Token: {refresh.access_token}")
            print(f"Refresh Token: {refresh}")

            # Attempt to retrieve tokens from cookies in response
            access_cookie = response.cookies.get('access_token')
            refresh_cookie = response.cookies.get('refresh')

            print("Cookies set in the response:")
            print(f"Access Token Cookie: {access_cookie}")
            print(f"Refresh Token Cookie: {refresh_cookie}")

            return response
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        

User = get_user_model()

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access_token')
        print(f"Access Token from cookies: {access_token}")

        # Blacklist the access token if present
        if access_token:
            try:
                parsed_access_token = AccessToken(access_token)
                user_id = request.user.id
                print(f"Extracted user ID: {user_id}")

                # Ensure the user exists
                user = User.objects.filter(id=user_id).first()
                if not user:
                    print(f"User with ID {user_id} not found.")
                    return Response({"error": "Invalid token user."}, status=status.HTTP_400_BAD_REQUEST)

                # Create or get OutstandingToken entry
                outstanding_access_token, created = OutstandingToken.objects.get_or_create(
                    jti=parsed_access_token['jti'],
                    defaults={
                        'token': access_token,  # Store the string representation
                        'user': user,
                        'expires_at': timezone.now(),  # Short lifetime
                    }
                )

                # Blacklist the token if it wasn't already blacklisted
                if not created:
                    print("Outstanding token already exists; blacklisting existing token.")
                    if not BlacklistedToken.objects.filter(token=outstanding_access_token).exists():
                        BlacklistedToken.objects.create(token=outstanding_access_token)
                        print("Access token blacklisted.")
                    else:
                        print("Access token is already blacklisted.")
            except Exception as e:
                print("Error blacklisting access token:", e)
                return Response({"error": "Failed to blacklist access token."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with the token refresh process
        response = super().post(request, *args, **kwargs)

        # Set the new access token in an HTTP-only cookie if the refresh was successful
        if response.status_code == status.HTTP_200_OK:
            new_access_token = response.data.get('access')
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=True,  # Change as needed for your environment
                samesite='Lax'
            )

        return response


class CustomBlacklistView(TokenBlacklistView):
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        self.permission_classes = [IsAuthenticated]
        # Log all cookies for debugging
        print("Cookies received:", request.COOKIES)
        
        # Retrieve the tokens from cookies
        refresh_token = request.COOKIES.get('refresh')
        access_token = request.COOKIES.get('access_token')

        print(f"Received refresh_token: {refresh_token}")
        print(f"Received access_token: {access_token}")

        try:

           # Create and blacklist the access token
            if access_token:
                try:
                    access_token = AccessToken(access_token)
                    
                    # Create OutstandingToken entry for the access token if it doesn't exist
                    outstanding_access_token, created = OutstandingToken.objects.get_or_create(
                        jti=access_token['jti'],
                        defaults={
                            'token': access_token,
                            'user': request.user,
                            'expires_at': timezone.now(),  # Short lifetime
                        }
                    )
                    
                    # Add to BlacklistedToken if not already blacklisted
                    if not BlacklistedToken.objects.filter(token=outstanding_access_token).exists():
                        BlacklistedToken.objects.create(token=outstanding_access_token)
                        print("Access token blacklisted.")
                    else:
                        print("Access token is already blacklisted.")
                except Exception as e:
                    print("Error blacklisting access token:", e)


            # Blacklist the refresh token if it exists
            if refresh_token:
                outstanding_refresh_token = OutstandingToken.objects.filter(token=refresh_token).first()
                if outstanding_refresh_token:
                    # Check if the token is already blacklisted
                    if not BlacklistedToken.objects.filter(token=outstanding_refresh_token).exists():
                        BlacklistedToken.objects.create(token=outstanding_refresh_token)
                        print(f"Blacklisted refresh_token: {outstanding_refresh_token.token}")
                    else:
                        print("Refresh token is already blacklisted.")
                else:
                    print("No outstanding refresh token found.")

            
            # Clear cookies after logout
            response = Response({"success": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('access_token')  # Clear the access token cookie
            response.delete_cookie('refresh')  # Clear the refresh token cookie
            print("Cookies cleared.")

            return response

        except Exception as e:
            print("An error occurred during logout:", str(e))
            return Response({
                "error": "An error occurred during logout.",
                "details": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, retrieving, creating, updating, and deleting users with JWT authentication and permissions.
    """
    
    # Apply JWT authentication to all actions
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        # Only allow admin users to list all users
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    # def retrieve(self, request, pk=None):
    #     # Only allow authenticated users to retrieve user profiles
    #     self.permission_classes = [IsAuthenticated]
    #     self.check_permissions(request)

    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset, pk=pk)
    #     serializer = UserSerializer(user)
    #     return Response(serializer.data)

    def create(self, request):
        # Allow anyone to create a new user account
        data = request.data
        # Manually hash the password before saving
        if 'password' in data:
            data['password'] = make_password(data['password'])
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # Only authenticated users can update their profiles
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        user = get_object_or_404(User, pk=pk)
        data = request.data
        
        # Hash password if it exists in the request
        if 'password' in data:
            data['password'] = make_password(data['password'])
            
        serializer = UserSerializer(user, data=data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def destroy(self, request, pk=None):
    #     # Only admin users can delete a user
    #     self.permission_classes = [IsAdminUser]
    #     self.check_permissions(request)

    #     user = get_object_or_404(User, pk=pk)
    #     user.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)



class AddressViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting addresses.
    """
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)

        # Filter addresses by the logged-in user
        queryset = Address.objects.all()
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        address = get_object_or_404(Address, pk=pk)  # Check if the address belongs to the user
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def create(self, request):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user to the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        address = get_object_or_404(Address, pk=pk, user=request.user)  # Ensure user owns the address
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        address = get_object_or_404(Address, pk=pk, user=request.user)  # Ensure user owns the address
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class PhysicalAddressViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting physical addresses.
    """
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)
        queryset = PhysicalAddress.objects.all()
        serializer = PhysicalAddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        queryset = PhysicalAddress.objects.all()
        physical_address = get_object_or_404(queryset, pk=pk, user=request.user)
        serializer = PhysicalAddressSerializer(physical_address)
        return Response(serializer.data)

    def create(self, request):
        
        serializer = PhysicalAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        physical_address = get_object_or_404(PhysicalAddress, pk=pk, user=request.user)
        serializer = PhysicalAddressSerializer(physical_address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        physical_address = get_object_or_404(PhysicalAddress, pk=pk, user=request.user)
        physical_address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CreditCardViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting credit cards.
    """
    authentication_classes = [JWTAuthentication]

    
    def list(self, request):
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)
        queryset = CreditCard.objects.all()
        serializer = CreditCardSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        queryset = CreditCard.objects.all()
        credit_card = get_object_or_404(queryset, pk=pk, use=request.user)
        serializer = CreditCardSerializer(credit_card)
        return Response(serializer.data)

    def create(self, request):
        serializer = CreditCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)
        serializer = CreditCardSerializer(credit_card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)
        credit_card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)