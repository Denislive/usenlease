# rentals/views.py
import jwt
from rest_framework.exceptions import NotAuthenticated
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


from .models import User, Address, PhysicalAddress, CreditCard, Message, Chat, Message
from .serializers import UserSerializer, AddressSerializer, PhysicalAddressSerializer, CreditCardSerializer, ChatSerializer, MessageSerializer

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
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer  # Adjust the import as necessary

from rest_framework.parsers import MultiPartParser, FormParser



from .models import OTP
from .serializers import OTPSerializer
import random
import smtplib
from email.mime.text import MIMEText
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

User = get_user_model()

class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        # Retrieve access and refresh tokens from cookies
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
                    # If there is an issue with the refresh token, raise an authentication error
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
    

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    # Define custom authentication class to use JWT authentication from cookies
    authentication_classes = [JWTAuthenticationFromCookie]
    

    def get_queryset(self):
        self.check_permissions(self.request)  
        # Filter chats by current logged-in user
        return Chat.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """Create a new chat with the logged-in user and specified participants."""
        sender = self.request.user
        recipient_ids = self.request.data.get('participants', [])

        # Ensure the logged-in user is included in participants
        participants = [sender]

        # Add recipients if they exist
        if recipient_ids:
            recipients = get_user_model().objects.filter(id__in=recipient_ids)
            participants.extend(recipients)

        # Save the chat with the combined participants
        serializer.save(participants=participants)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthenticationFromCookie]  # Use JWT authentication from cookies
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        """Retrieve messages for a specific chat or for the logged-in user."""
        self.check_permissions(self.request)  # Check user permissions before fetching data
        chat_id = self.request.query_params.get("chat_id")
        
        if chat_id:
            # If a chat ID is provided, return messages for that specific chat
            return Message.objects.filter(chat_id=chat_id, is_deleted=False).order_by("sent_at")
        
        # Otherwise, return messages where the user is either sender or receiver
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user),
            is_deleted=False
        ).order_by("sent_at")

    @transaction.atomic
    def perform_create(self, serializer):
        """Ensure chat exists between sender and receiver before creating a message."""
        sender = self.request.user
        receiver_id = self.request.data.get("receiver")

        # Validate that a receiver ID is provided
        if not receiver_id:
            raise ValueError("Receiver ID is required to send a message.")
        
        try:
            # Attempt to retrieve the receiver user object
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            # Raise error if the receiver does not exist
            raise ValueError("Receiver not found.")

        # Check if a chat already exists between the sender and receiver
        chat = Chat.objects.filter(participants=sender).filter(participants=receiver).distinct()
        
        if not chat.exists():
            # If no chat exists, create a new one
            chat = Chat.objects.create()
            chat.participants.set([sender, receiver])
        else:
            chat = chat.first()

        # Save the message associated with the chat
        serializer.save(sender=sender, receiver=receiver, chat=chat)

    def delete_message(self, request, pk=None):
        try:
            # Mark the message as deleted rather than removing it
            message = Message.objects.get(id=pk, sender=self.request.user)
            message.is_deleted = True
            message.save()
            return Response({"message": "Message deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Message.DoesNotExist:
            # Handle the case where the message is not found
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)


class AllChatsViewSet(viewsets.ViewSet):

    authentication_classes = [JWTAuthenticationFromCookie]  # Use JWT authentication from cookies

    def list(self, request):
        # Get all chats for the user
        self.check_permissions(request)  # Ensure the user has permission to view chats
        chats = Chat.objects.filter(participants=request.user)  # Get chats where user is a participant
        serializer = ChatSerializer(chats, many=True)  # Serialize the chat data
        return Response(serializer.data)  # Return serialized chat data


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

        # Expire all existing OTPs for the user
        OTP.objects.filter(user=user, expired=False).update(expired=True)

        # Generate a new OTP and save it in the database
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
            # Handle any errors that occur while sending the email
            return Response({"error": "Failed to send OTP", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        # Retrieve the user's email and OTP from the request
        email = request.data.get("email")
        entered_otp = request.data.get("otp")
        print(email, entered_otp)

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
            
            # Check if the OTP is expired and mark it as expired if necessary
            if otp_instance.is_expired():
                otp_instance.expire()  # Mark OTP as expired
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            if otp_instance.code == entered_otp:
                # OTP verified successfully; activate the user's account
                user.is_active = True
                user.save()
                otp_instance.expire()  # Mark OTP as expired after successful verification
                print("User activated")
                return Response({"message": "OTP verified successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        except OTP.DoesNotExist:
            # If OTP does not exist, return an error
            return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)
class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request):
        # Get email and password from the request data
        email = request.data.get("email")
        password = request.data.get("password")
        
        # Authenticate the user with the provided credentials
        user = authenticate(request, email=email, password=password)

        if user:
            # Create refresh token for the user
            refresh = RefreshToken.for_user(user)

            # Serialize the user details
            user_data = UserSerializer(user).data

            # Prepare the response data (excluding sensitive information)
            response_data = {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_authenticated": user.is_authenticated
            }
            
            # Create a response with the user data
            response = Response(response_data, status=status.HTTP_200_OK)

            # Set the access token in an HTTP-only cookie
            response.set_cookie(
                key="token", 
                value=str(refresh.access_token),
                httponly=True,  # Cookie will not be accessible via JavaScript
                secure=True,  # Change to True if using HTTPS in production
                samesite='None',  # To allow cross-site cookies
                path="/"
            )

            # Set the refresh token as an HTTP-only cookie
            response.set_cookie(
                key="refresh", 
                value=str(refresh),
                httponly=True,  # Cookie will not be accessible via JavaScript
                secure=True,  # Change to True if using HTTPS in production
                samesite='None',  # To allow cross-site cookies
                path="/"
            )

            # Retrieve and log tokens from cookies in the response (for debugging)
            access_cookie = response.cookies.get('token')
            refresh_cookie = response.cookies.get('refresh')  # Updated to 'refresh_token'

            return response
        else:
            # Return an error response if authentication fails
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Retrieve the refresh token from the cookies
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate the refresh token
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            # Prepare the response with the new access token
            response = Response({"message": "Token refreshed successfully."})
            response.set_cookie(
                key="token",  # Set the new access token in a cookie
                value=new_access_token,
                httponly=True,  # Cookie will not be accessible via JavaScript
                secure=True,  # Set to True in production (HTTPS)
                samesite='None',  # To allow cross-site cookies
                path="/"
            )
            return response
        except TokenError as e:
            # Return an error if the refresh token is invalid
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)


class CustomLogoutView(APIView):

    def post(self, request):
        # Retrieve the access and refresh tokens from the cookies
        access_token = request.COOKIES.get('token')
        refresh_token = request.COOKIES.get('refresh')

        if access_token is None:
            return Response({'detail': 'No access token provided.'}, status=400)

        if refresh_token is None:
            return Response({'detail': 'No refresh token provided.'}, status=400)

        try:
            # Create a RefreshToken object from the refresh token
            token = RefreshToken(refresh_token)

            # Retrieve the OutstandingToken instance for the refresh token
            outstanding_token = OutstandingToken.objects.get(token=token)

            # Blacklist the outstanding token to prevent further use
            BlacklistedToken.objects.create(token=outstanding_token)

            # Optional: Clear the refresh token and access token cookies
            response = Response({'detail': 'Token has been blacklisted.'})
            response.delete_cookie('refresh')  # Remove the refresh token cookie
            response.delete_cookie('token')  # Remove the access token cookie
            
            return response

        except OutstandingToken.DoesNotExist:
            # Return an error if the outstanding token is not found
            return Response({'detail': 'Outstanding token not found.'}, status=404)
        except TokenError as e:
            # Return an error if there's a token-related issue
            print(f'TokenError: {str(e)}')
            return Response({'detail': f'Token error: {str(e)}'}, status=400)
        except Exception as e:
            # Return a general error response if an unexpected error occurs
            print(f'General Exception: {str(e)}')
            return Response({'detail': f'An error occurred: {str(e)}'}, status=500) 

class UserViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, retrieving, creating, updating, and deleting users with JWT authentication and permissions.
    """
    
    # Apply JWT authentication to all actions
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        """
        List all users. Only admin users can perform this action.
        """
        # Only allow admin users to list all users
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        queryset = User.objects.all()  # Retrieve all users
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve the details of the authenticated user.
        """
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated("Authentication required.")  # Ensure user is authenticated

        serializer = UserSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        """
        Allow anyone to create a new user account.
        """
        # Retrieve data from the request
        data = request.data
        first_name = data['first_name']
        last_name = data['last_name']
        
        # Manually hash the password before saving
        if 'password' in data:
            data['password'] = make_password(data['password'])

        # Set the username based on first and last name
        data['username'] = "{} {}".format(first_name, last_name)
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # Save the user to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return created user data
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Handle validation errors

    def update(self, request, pk=None):
        """
        Update a user's profile. Only authenticated users can update their own profile.
        """
        # Only authenticated users can update their profiles
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        user = get_object_or_404(User, pk=pk)  # Retrieve the user or raise 404 if not found
        data = request.data
        print("update data", data)

        # Hash the password if it's provided in the request
        if 'password' in data:
            data['password'] = make_password(data['password'])

        # Allow partial updates
        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()  # Save the updated user data
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a user. Only admin users can perform this action.
        """
        # Only admin users can delete a user
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)

        user = get_object_or_404(User, pk=pk)  # Retrieve the user or raise 404
        user.delete()  # Delete the user from the database
        return Response(status=status.HTTP_204_NO_CONTENT)  # Return no content response


class AddressViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting addresses.
    """
    # Use JWT authentication for all actions
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        List all addresses. Only authenticated users and admins can access this view.
        """
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)

        # Retrieve all addresses
        queryset = Address.objects.all()
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve the details of a specific address. Only authenticated users can access.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        # Retrieve the address or raise 404
        address = get_object_or_404(Address, pk=pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new address. Only authenticated users can create an address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        # Serialize the address data and associate the user with the address
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the logged-in user with the address
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing address. The user must be authenticated and own the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        # Retrieve the address or raise 404 if it does not belong to the user
        address = get_object_or_404(Address, pk=pk, user=request.user)
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated address data
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete an address. The user must be authenticated and own the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        # Retrieve the address or raise 404 if it does not belong to the user
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.delete()  # Delete the address
        return Response(status=status.HTTP_204_NO_CONTENT)
class PhysicalAddressViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting physical addresses.
    """
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        """
        List all physical addresses. Only authenticated users and admins can access this view.
        """
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)  # Check user permissions

        queryset = PhysicalAddress.objects.all()  # Retrieve all physical addresses
        serializer = PhysicalAddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve the details of a specific physical address.
        Only the user who owns the address can retrieve it.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)  # Ensure the user is authenticated

        # Retrieve the specific physical address or raise 404 if it does not belong to the user
        physical_address = get_object_or_404(PhysicalAddress, pk=pk, user=request.user)
        serializer = PhysicalAddressSerializer(physical_address)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new physical address for the authenticated user.
        """
        # Serialize the address data and save it with the logged-in user
        serializer = PhysicalAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the physical address with the user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing physical address. Only the owner of the address can update it.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)  # Ensure the user is authenticated

        # Retrieve the physical address or raise 404 if the user does not own it
        physical_address = get_object_or_404(PhysicalAddress, pk=pk, user=request.user)
        serializer = PhysicalAddressSerializer(physical_address, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated address
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a specific physical address. The user must own the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)  # Ensure the user is authenticated

        # Retrieve the physical address or raise 404 if the user does not own it
        physical_address = get_object_or_404(PhysicalAddress, pk=pk, user=request.user)
        physical_address.delete()  # Delete the physical address
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreditCardViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting credit cards.
    """
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        List all credit cards. Only authenticated users and admins can access this view.
        """
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)  # Check user permissions

        queryset = CreditCard.objects.all()  # Retrieve all credit cards
        serializer = CreditCardSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve the details of a specific credit card. Only the user who owns the card can retrieve it.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)  # Ensure the user is authenticated

        # Retrieve the specific credit card or raise 404 if it does not belong to the user
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)
        serializer = CreditCardSerializer(credit_card)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new credit card for the authenticated user.
        """
        # Serialize the credit card data and save it
        serializer = CreditCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the credit card with the user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing credit card. Only the owner of the card can update it.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)  # Ensure the user is authenticated

        # Retrieve the credit card or raise 404 if the user does not own it
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)
        serializer = CreditCardSerializer(credit_card, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated credit card
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a specific credit card. The user must own the card.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)  # Ensure the user is authenticated

        # Retrieve the credit card or raise 404 if the user does not own it
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)
        credit_card.delete()  # Delete the credit card
        return Response(status=status.HTTP_204_NO_CONTENT)
