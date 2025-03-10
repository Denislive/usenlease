# rentals/views.py
import jwt
from rest_framework.exceptions import NotAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password

from rest_framework import viewsets
from rest_framework.views import APIView
from datetime import date
from rest_framework.response import Response
from rest_framework import status

from rest_framework.exceptions import ValidationError
from django.db.models import Q


from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import IntegrityError


from .models import User, Address, PhysicalAddress, CreditCard, Message
from .serializers import UserSerializer, AddressSerializer, PhysicalAddressSerializer, CreditCardSerializer, MessageSerializer, ContactSerializer

# views.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView, TokenVerifyView


from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail


from django.http import JsonResponse


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

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer
from django.db.models import Q

from .models import OTP
from equipment_management.models import Cart, Equipment, CartItem, Order, OrderItem
from .serializers import OTPSerializer
import random
import smtplib
from email.mime.text import MIMEText
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.db import transaction
User = get_user_model()


from rest_framework import viewsets, permissions, response
from django.db.models import Sum, Count
from .models import User

from rest_framework import viewsets
from equipment_management.models import Equipment, Order, Review
from rest_framework.response import Response

from django.db.models import Avg, Sum, Count, F, Prefetch

from rest_framework.views import APIView
from .models import CompanyInfo
from .serializers import CompanyInfoSerializer


class CompanyInfoView(APIView):

    def get(self, request):
        try:
            company_info = CompanyInfo.objects.first()
            serializer = CompanyInfoSerializer(company_info)
            return Response(serializer.data)
        except CompanyInfo.DoesNotExist:
            return Response({"error": "Company information not found"}, status=404)


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

class ContactViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for handling contact form submissions.
    """
    def create(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            # Save the contact data to the database (optional)
            serializer.save()
            
            # Send an email
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            message = serializer.validated_data['message']

            # Prepare email content
            subject = f"New Customer Inquiry {name}"
            message_body = (
                f"Message from {name} ({email}):\n\n"
                f"{message}\n\n"
                f"If you have any questions, please feel free to reply to this email.\n\n"
                f"Best regards,\n"
                f"The Use And Lease Team"
            )

            try:
                # Prepare the email
                msg = MIMEText(message_body)
                msg['Subject'] = subject
                msg['From'] = f"{email}"
                msg['To'] = settings.RECIPIENT_LIST  # Assuming the first recipient in the list for now

                # Send the email using SMTP
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)
                server.quit()

                return Response({"detail": "Message sent successfully."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": "Message could not be sent.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportViewSet(viewsets.ViewSet):

    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        user = request.user
        report_data = {}

        if user.role == 'lessor':
            # Collect data for lessor
            total_equipments = Equipment.objects.filter(owner=user).count()
            total_orders = Order.objects.filter(cart__user=user).count()
            total_rented_items = Order.objects.filter(cart__user=user, status='rented').count()
            total_revenue = Order.objects.filter(cart__user=user).aggregate(Sum('order_total_price'))['order_total_price__sum'] or 0.0
            total_reviews = Review.objects.filter(equipment__owner=user).count()
            total_available_equipment = Equipment.objects.filter(owner=user, is_available=True).count()
            total_rented_equipment = Equipment.objects.filter(owner=user).aggregate(Sum('available_quantity'))['available_quantity__sum'] or 0
            total_canceled_orders = Order.objects.filter(cart__user=user, status='canceled').count()
            total_completed_orders = Order.objects.filter(cart__user=user, status='completed').count()
            average_rating = Review.objects.filter(equipment__owner=user).aggregate(Avg('rating'))['rating__avg'] or 0.0
            total_equipment_types = Equipment.objects.filter(owner=user).values('category').distinct().count()

            report_data = {
                
                'total_equipments': total_equipments,
                'total_orders': total_orders,
                'total_rented_items': total_rented_items,
                'total_revenue': total_revenue,
                'total_reviews': total_reviews,
                'total_available_equipment': total_available_equipment,
                'total_rented_equipment': total_rented_equipment,
                'average_rating': average_rating,
                'total_canceled_orders': total_canceled_orders,
                'total_completed_orders': total_completed_orders,
                'total_equipment_types': total_equipment_types,
            }

        elif user.role == 'lessee':
            # Collect data for lessee
            total_orders = Order.objects.filter(user=user).count()
            total_rented_items = Order.objects.filter(user=user, status='rented').count()
            total_cart_items = CartItem.objects.filter(cart__user=user).count()
            total_reviews = Review.objects.filter(user=user).count()
            average_rating_given = Review .objects.filter(user=user).aggregate(Avg('rating'))['rating__avg'] or 0.0
            total_canceled_orders = Order.objects.filter(user=user, status='canceled').count()
            total_completed_orders = Order.objects.filter(user=user, status='completed').count()
            total_spending = Order.objects.filter(user=user).aggregate(Sum('order_total_price'))['order_total_price__sum'] or 0.0
            total_equipment_types_rented = OrderItem.objects.filter(order__user=user).values('item__category').distinct().count()

            report_data = {
                'total_orders': total_orders,
                'total_rented_items': total_rented_items,
                'total_cart_items': total_cart_items,
                'total_reviews': total_reviews,
                'average_rating_given': average_rating_given,
                'total_canceled_orders': total_canceled_orders,
                'total_completed_orders': total_completed_orders,
                'total_spending': total_spending,
                'total_equipment_types_rented': total_equipment_types_rented,
            }
        return Response(report_data)

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    authentication_classes = [JWTAuthenticationFromCookie]

    def get_queryset(self):
        self.check_permissions(self.request)
        # Filter chats by the current logged-in user
        return Chat.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """Create a new chat with the logged-in user and specified participants, or prevent creating duplicate chats."""
        sender = self.request.user
        participants_ids = self.request.data.get('participants', [])

        # Ensure the logged-in user is included in the participants list
        participants = [sender.id]
        if participants_ids:
            participants.extend(participants_ids)

        # Prevent chat creation if the logged-in user is the only participant
        if len(participants) < 2:
            raise ValidationError("You must include at least one other participant.")

        # Check if the sender is trying to contact themselves
        if sender.id in participants_ids:
            raise ValidationError("You cannot contact yourself.")

        # Check if a chat with these participants already exists
        existing_chats = Chat.objects.filter(participants=sender)
        for participant_id in participants_ids:
            existing_chats = existing_chats.filter(participants=participant_id)

        if existing_chats.exists():
            raise ValidationError("A chat already exists with these participants.")

        # Save the chat with the combined participants if no existing chat is found
        serializer.save(participants=[sender] + list(User.objects.filter(id__in=participants_ids)))

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthenticationFromCookie]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve messages for a specific chat or for the logged-in user."""
        self.check_permissions(self.request)
        chat_id = self.request.query_params.get("chat_id")
        
        if chat_id:
            return Message.objects.filter(chat_id=chat_id, is_deleted=False).order_by("sent_at")
        
        # Messages where the user is either sender or receiver
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user),
            is_deleted=False
        ).order_by("sent_at")

    @transaction.atomic
    def perform_create(self, serializer):
        """Ensure chat exists between sender and receiver before creating a message."""
        sender = self.request.user
        receiver_id = self.request.data.get("receiver")

        if not receiver_id:
            raise ValueError("Receiver ID is required to send a message.")
        
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            raise ValueError("Receiver not found.")

        # Check if a chat already exists between the sender and receiver
        chat = Chat.objects.filter(participants=sender).filter(participants=receiver).distinct()
        
        if not chat.exists():
            # Create a new chat
            chat = Chat.objects.create()
            chat.participants.set([sender, receiver])
        else:
            chat = chat.first()

        # Save the message associated with the chat
        serializer.save(sender=sender, receiver=receiver, chat=chat)

    def delete_message(self, request, pk=None):
        try:
            message = Message.objects.get(id=pk, sender=self.request.user)
            message.is_deleted = True
            message.save()
            return Response({"message": "Message deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Message.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)


class AllChatsViewSet(viewsets.ViewSet):

    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        # Get all chats for the user
        self.check_permissions(request)  
        chats = Chat.objects.filter(participants=request.user)
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)


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
            return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Serialize user data
            response_data = {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_authenticated": user.is_authenticated,
                "image": user.image.url if user.image else None,
            }
            response = Response(response_data, status=status.HTTP_200_OK)

            # Set tokens in cookies
            response.set_cookie(
                key="token",
                value=str(refresh.access_token),
                httponly=True,
                secure=True,
                samesite='None',
                path="/"
            )
            response.set_cookie(
                key="refresh",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='None',
                path="/"
            )

            # Sync cart
            cart_data = request.data.get("cart", [])
            if cart_data:
                try:
                    self.sync_cart_with_db(user, cart_data)
                except Exception as e:
                    return Response(
                        {"error": f"Error syncing cart: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return response

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    def sync_cart_with_db(self, user, cart_data):
        """Sync the cart items from the frontend to the database for the user."""
        user_cart, _ = Cart.objects.get_or_create(user=user)

        for item_data in cart_data:
            try:
                item_info = item_data.get("item")
                item_id = item_info.get("id")
                item_quantity = item_data.get("quantity", 1)
                start_date = item_data.get("start_date")
                end_date = item_data.get("end_date")

                # Validate dates
                if not start_date or not end_date:
                    continue
                start_date = date.fromisoformat(start_date)
                end_date = date.fromisoformat(end_date)

                if start_date < date.today() or start_date > end_date:
                    continue

                # Validate equipment existence
                equipment = Equipment.objects.filter(id=item_id).first()
                if not equipment:
                    continue

                # Validate quantity
                if item_quantity <= 0:
                    continue

                available_quantity = equipment.is_available_for_dates(start_date, end_date)
                if item_quantity > available_quantity:
                    continue

                # Check for existing cart item
                cart_item = CartItem.objects.filter(cart=user_cart, item=equipment).first()
                if cart_item:
                    # Overwrite dates and update quantity
                    cart_item.start_date = start_date
                    cart_item.end_date = end_date
                    cart_item.quantity = item_quantity
                    cart_item.save()
                else:
                    # Create a new cart item
                    CartItem.objects.create(
                        cart=user_cart,
                        item=equipment,
                        start_date=start_date,
                        end_date=end_date,
                        quantity=item_quantity
                    )
            except Exception as e:
                raise Exception(f"Error syncing item {item_data}: {str(e)}")





class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            response = Response({"message": "Token refreshed successfully."})
            response.set_cookie(
                key="token",
                value=new_access_token,
                httponly=True,
                secure=True,  # Set to True in production
                samesite='None',
                path="/"
            )
            return response
        except TokenError as e:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)



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


class CheckPhoneNumberView(APIView):
    """
    API endpoint to check if a phone number is already registered.
    """
    def get(self, request):
        phone_number = request.query_params.get('phone', None)
        if not phone_number:
            return JsonResponse({'error': 'Phone parameter is required.'}, status=400)

        exists = User.objects.filter(phone_number=phone_number).exists()
        return JsonResponse({'exists': exists})

class CheckEmailView(APIView):
    """
    API endpoint to check if an email is already registered.
    """
    def get(self, request):
        email = request.query_params.get('email', None)
        if not email:
            return JsonResponse({'error': 'Email parameter is required.'}, status=400)

        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'exists': exists})

class UserViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, retrieving, creating, updating, and deleting users with JWT authentication and permissions.
    """
    
    # Apply JWT authentication to all actions
    authentication_classes = [JWTAuthenticationFromCookie]

    def list(self, request):
        # Only allow admin users to list all users
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)  # Ensure permission check is applied

        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated("Authentication required.")

        serializer = UserSerializer(user)
        return Response(serializer.data)


    def create(self, request):
        # Allow anyone to create a new user account
        data = request.data
        first_name = data['first_name']
        last_name = data['last_name']
        # Manually hash the password before saving
        if 'password' in data:
            data['password'] = make_password(data['password'])

        data['username'] = "{} {}".format(first_name, last_name)
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
        print("update data", data)

        
        # Hash password if it exists in the request
        if 'password' in data:
            data['password'] = make_password(data['password'])
            
        serializer = UserSerializer(user, data=data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # Only admin users can delete a user
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
    authentication_classes = [JWTAuthenticationFromCookie]

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