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


# Custom authentication class that uses JWT tokens stored in cookies
class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        """
        Authenticate a user based on JWT tokens stored in cookies.
        """
        # Retrieve tokens from cookies
        access_token = request.COOKIES.get('token')  # Access token cookie
        refresh_token = request.COOKIES.get('refresh')  # Refresh token cookie

        # If no access token is found, return None (unauthenticated)
        if not access_token:
            return None

        try:
            # Validate the access token
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            # Handle invalid or expired access token
            if refresh_token:
                try:
                    # Use the refresh token to generate a new access token
                    refresh = RefreshToken(refresh_token)
                    new_access_token = str(refresh.access_token)

                    # Set the new access token in the response cookies
                    response = self.get_user_response(request)
                    response.set_cookie('token', new_access_token, httponly=True, secure=True)

                    # Validate the new access token
                    validated_token = self.get_validated_token(new_access_token)
                    return self.get_user(validated_token), validated_token
                except TokenError:
                    # Refresh token is invalid or expired
                    raise AuthenticationFailed(_('Token is invalid or expired.'))

            # No refresh token provided, authentication fails
            raise AuthenticationFailed(_('Token is expired and no refresh token is provided.'))

    def get_user_response(self, request):
        """
        Helper method to return a response object for setting cookies.
        """
        from rest_framework.response import Response
        return Response()


# ViewSet for managing chats
class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()  # Query all chat objects
    serializer_class = ChatSerializer  # Serializer for chat objects
    authentication_classes = [JWTAuthenticationFromCookie]

    def get_queryset(self):
        """
        Retrieve chats for the authenticated user.
        """
        self.check_permissions(self.request)
        return Chat.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new chat with the logged-in user and specified participants.
        """
        sender = self.request.user
        recipient_ids = self.request.data.get('participants', [])
        participants = [sender]

        # Add recipients to the participants list
        if recipient_ids:
            recipients = get_user_model().objects.filter(id__in=recipient_ids)
            participants.extend(recipients)

        # Save the chat with all participants
        serializer.save(participants=participants)


# ViewSet for managing messages
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()  # Query all message objects
    serializer_class = MessageSerializer  # Serializer for message objects
    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve messages for a specific chat or the authenticated user.
        """
        self.check_permissions(self.request)
        chat_id = self.request.query_params.get("chat_id")

        if chat_id:
            # Messages for a specific chat
            return Message.objects.filter(chat_id=chat_id, is_deleted=False).order_by("sent_at")

        # Messages where the user is sender or receiver
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user),
            is_deleted=False
        ).order_by("sent_at")

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Ensure a chat exists between sender and receiver before creating a message.
        """
        sender = self.request.user
        receiver_id = self.request.data.get("receiver")

        if not receiver_id:
            raise ValueError("Receiver ID is required to send a message.")

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            raise ValueError("Receiver not found.")

        # Check if a chat exists between sender and receiver
        chat = Chat.objects.filter(participants=sender).filter(participants=receiver).distinct()
        if not chat.exists():
            # Create a new chat if it doesn't exist
            chat = Chat.objects.create()
            chat.participants.set([sender, receiver])
        else:
            chat = chat.first()

        # Save the message associated with the chat
        serializer.save(sender=sender, receiver=receiver, chat=chat)

    def delete_message(self, request, pk=None):
        """
        Soft delete a message sent by the authenticated user.
        """
        try:
            message = Message.objects.get(id=pk, sender=self.request.user)
            message.is_deleted = True
            message.save()
            return Response({"message": "Message deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Message.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)


# ViewSet for handling OTP generation and verification
class OTPViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def generate_otp(self, request):
        """
        Generate and send a one-time password (OTP) to a user's email.
        """
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Expire any existing OTPs
        OTP.objects.filter(user=user, expired=False).update(expired=True)

        # Generate and save a new OTP
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=otp_code)

        # Send OTP via email
        try:
            subject = "Email Verification"
            message_body = f"Your OTP code is: {otp_code}"
            msg = MIMEText(message_body)
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_HOST_USER
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
        """
        Verify the OTP provided by the user.
        """
        email = request.data.get("email")
        entered_otp = request.data.get("otp")

        if not email or not entered_otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user and verify OTP
        try:
            user = User.objects.get(email=email)
            otp_instance = OTP.objects.filter(user=user, code=entered_otp).latest('created_at')
            if otp_instance.is_expired():
                otp_instance.expire()
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
            user.is_active = True
            user.save()
            otp_instance.expire()
            return Response({"message": "OTP verified successfully!"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except OTP.DoesNotExist:
            return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)
class UserViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, retrieving, creating, updating, and deleting users with JWT authentication and permissions.
    """

    # Apply JWT authentication to all actions
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        """
        List all users.
        Only accessible by admin users.
        """
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)  # Enforce admin-only access

        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve the authenticated user's details.
        """
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated("Authentication required.")
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new user account.
        Accessible by anyone.
        """
        data = request.data
        first_name = data['first_name']
        last_name = data['last_name']
        
        # Ensure password is hashed before saving
        if 'password' in data:
            data['password'] = make_password(data['password'])

        # Auto-generate a username using first and last name
        data['username'] = "{} {}".format(first_name, last_name)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update a user's details. Accessible by authenticated users only.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)

        user = get_object_or_404(User, pk=pk)
        data = request.data

        # Hash password if included in the update
        if 'password' in data:
            data['password'] = make_password(data['password'])

        serializer = UserSerializer(user, data=data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a user account. Only accessible by admin users.
        """
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)

        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting addresses.
    """
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        List all addresses, accessible by admin or authenticated users.
        """
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)

        # Filter addresses by the logged-in user
        queryset = Address.objects.all()
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve details of a specific address. Only accessible by the user who owns the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        address = get_object_or_404(Address, pk=pk, user=request.user)  # Ensure user owns the address
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new address for the logged-in user.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the address with the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing address. Accessible only by the user who owns the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        address = get_object_or_404(Address, pk=pk, user=request.user)  # Ensure user owns the address
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a specific address. Accessible only by the user who owns the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        address = get_object_or_404(Address, pk=pk, user=request.user)  # Ensure user owns the address
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PhysicalAddressViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing, retrieving, updating, and deleting physical addresses.
    """
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        """
        List all physical addresses. Accessible by admin or authenticated users.
        """
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)
        queryset = PhysicalAddress.objects.all()
        serializer = PhysicalAddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific physical address. Accessible only by the user who owns the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        physical_address = get_object_or_404(PhysicalAddress, pk=pk, user=request.user)  # Ensure user owns the address
        serializer = PhysicalAddressSerializer(physical_address)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new physical address for the logged-in user.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        serializer = PhysicalAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate physical address with the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing physical address. Accessible only by the user who owns the address.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        physical_address = get_object_or_404(PhysicalAddress, pk=pk, user=request.user)
        serializer = PhysicalAddressSerializer(physical_address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a physical address. Accessible only by the user who owns the address.
        """
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
        """
        List all credit cards. Accessible by admin or authenticated users.
        """
        self.permission_classes = [IsAdminUser, IsAuthenticated]
        self.check_permissions(request)
        queryset = CreditCard.objects.all()
        serializer = CreditCardSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific credit card. Only accessible by the user who owns the card.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)  # Ensure user owns the credit card
        serializer = CreditCardSerializer(credit_card)
        return Response(serializer.data)

    def create(self, request):
        """
        Create a new credit card record for the logged-in user.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        serializer = CreditCardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the card with the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Update an existing credit card. Accessible only by the user who owns the card.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)
        serializer = CreditCardSerializer(credit_card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a credit card record. Accessible only by the user who owns the card.
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        credit_card = get_object_or_404(CreditCard, pk=pk, user=request.user)
        credit_card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
