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
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView, TokenVerifyView


from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import UserSerializer


from django.utils import timezone
from datetime import timedelta, datetime
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.exceptions import TokenError


from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer  # Adjust the import as necessary



from .models import OTP
from .serializers import OTPSerializer
import random
import smtplib
from email.mime.text import MIMEText
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model

User = get_user_model()

class OTPViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def generate_otp(self, request):
        # Retrieve email from the request
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP and save it in the database
        otp_code = str(random.randint(100000, 999999))
        otp_instance = OTP.objects.create(user=user, code=otp_code)
        otp_instance.save()

        # Prepare email content
        subject = "Email Verification"
        message_body = (
            f"Hello {user.email},\n\n"
            f"Thank you for signing up with us! To activate your account, please use the following OTP code:\n\n"
            f"{otp_code}\n\n"
            f"If you did not request this OTP, please ignore this message.\n\n"
            f"Thank you for choosing our service!\n\n"
            f"Best regards,\n"
            f"The Use And Lease Team"
        )

        # Send email
        try:
            msg = MIMEText(message_body)
            msg['Subject'] = subject
            msg['From'] = f"Use N Lease <{settings.EMAIL_HOST_USER}>"
            msg['To'] = user.email

            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)
            server.quit()
            return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to send OTP", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        # Retrieve the user's email and OTP from the request
        email = request.data.get("email")
        entered_otp = request.data.get("otp")

        if not email or not entered_otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Verify OTP
        try:
            otp_instance = OTP.objects.filter(user=user, code=entered_otp).latest('created_at')
            if otp_instance.is_expired():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            if otp_instance.code == entered_otp:
                # OTP verified successfully; activate the user's account
                user.is_active = True
                user.save()
                print("user activated")
                return Response({"message": "OTP verified successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        except OTP.DoesNotExist:
            return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            # Create refresh token for the user
            refresh = RefreshToken.for_user(user)

            # Serialize the user details
            user_data = UserSerializer(user).data

            response_data = {
                "id": user.id,
                "username": user.username,
                "is_authenticated": user.is_authenticated  # Include all user details here
            }
            response = Response(response_data, status=status.HTTP_200_OK)

            # Set the access token in an HTTP-only cookie
            response.set_cookie(
                key="token", 
                value=str(refresh.access_token),
                httponly=True,
                secure=True,  # Change to True if using HTTPS in production
                samesite='None',
                path="/"
            )

            # Set the refresh token as an HTTP-only cookie
            response.set_cookie(
                key="refresh", 
                value=str(refresh),
                httponly=True,
                secure=True,  # Change to True if using HTTPS in production
                samesite='None',
                path="/"
            )

            # Log tokens for verification
            print("Tokens before setting cookies:")
            print(f"Access Token: {refresh.access_token}")
            print(f"Refresh Token: {refresh}")

            # Retrieve and log tokens from cookies in the response
            access_cookie = response.cookies.get('token')
            refresh_cookie = response.cookies.get('refresh')  # Updated to 'refresh_token'

            print("Cookies set in the response:")
            print(f"Access Token Cookie: {access_cookie}")
            print(f"Refresh Token Cookie: {refresh_cookie}")

            return response
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# class CustomTokenVerifyView(TokenVerifyView):
#     """
#     Custom token verification view that retrieves the token from cookies.
#     """
#     permission_classes = [AllowAny]
    
#     def post(self, request, *args, **kwargs):   
#         # Attempt to get the token from cookies
#         token = request.COOKIES.get('token')

#         if token is None:
#             return Response({'detail': 'No access token provided.'}, status=400)

        
        
#         # If no token is found in cookies, return an error response
#         if not token:
#             return Response({"detail": "Token not provided in cookies."}, status=status.HTTP_400_BAD_REQUEST)
        
#         # Update request data with token from cookies for verification
#         request.data['token'] = token
#         return super().post(request, *args, **kwargs)  # Call the parent method to handle verification


class CustomLogoutView(APIView):

    def post(self, request):
        # Retrieve the refresh token from the cookies
        access_token = request.COOKIES.get('token')
        refresh_token = request.COOKIES.get('refresh')

        if access_token is None:
            return Response({'detail': 'No access token provided.'}, status=400)

        if refresh_token is None:
            return Response({'detail': 'No refresh token provided.'}, status=400)

        try:
            # Create a RefreshToken object
            token = RefreshToken(refresh_token)

            # Retrieve the OutstandingToken instance
            outstanding_token = OutstandingToken.objects.get(token=token)

            # Blacklist the outstanding token
            BlacklistedToken.objects.create(token=outstanding_token)

            # Optional: Clear the refresh token cookie
            response = Response({'detail': 'Token has been blacklisted.'})
            response.delete_cookie('refresh')  # Ensure the correct cookie name is used
            response.delete_cookie('token')  # Ensure the correct cookie name is used
            
            return response

        except OutstandingToken.DoesNotExist:
            return Response({'detail': 'Outstanding token not found.'}, status=404)
        except TokenError as e:
            print(f'TokenError: {str(e)}')
            return Response({'detail': f'Token error: {str(e)}'}, status=400)
        except Exception as e:
            print(f'General Exception: {str(e)}')
            return Response({'detail': f'An error occurred: {str(e)}'}, status=500) 


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