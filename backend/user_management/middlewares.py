# from django.utils.deprecation import MiddlewareMixin
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from rest_framework.exceptions import AuthenticationFailed

# class JWTRefreshMiddleware(MiddlewareMixin):
#     def process_request(self, request):

#         # Retrieve tokens from cookies
#         access_token = request.COOKIES.get('token')  # Access token cookie
#         refresh_token = request.COOKIES.get('refresh')  # Refresh token cookie

      
#         # If no access token is present, return None (unauthenticated)
#         if not access_token and not refresh_token:
#             return

#         if access_token:
#             try:
#                 # Try to validate the access token
#                 jwt_auth = JWTAuthentication()
#                 validated_token = jwt_auth.get_validated_token(access_token)
#                 request.user = jwt_auth.get_user(validated_token)
#                 request.auth = validated_token
#                 return
#             except InvalidToken as e:
#                 print(f"Access token validation failed: {str(e)}")

#         if refresh_token:
#             try:
#                 # Attempt to get a new access token using the refresh token
#                 refresh = RefreshToken(refresh_token)
#                 new_access_token = str(refresh.access_token)

#                 response = self.get_response(request)

#                 # Set the new access token in the cookies
#                 response.set_cookie(
#                     key='token',
#                     value=new_access_token,
#                     httponly=True,
#                     secure=True,
#                     samesite='None',
#                     path="/",
#                     max_age=2 * 60  # 15 minutes
#                 )
#                 print("New access token set in cookies.")

#                 # Validate the new access token
#                 jwt_auth = JWTAuthentication()
#                 validated_token = jwt_auth.get_validated_token(new_access_token)
#                 request.user = jwt_auth.get_user(validated_token)
#                 request.auth = validated_token
#                 print("New access token is valid.")
#                 return response
#             except TokenError as e:
#                 print(f"Failed to refresh access token: {str(e)}")
#                 raise AuthenticationFailed('Refresh token is invalid or expired.')

#         print("Both access and refresh tokens are invalid.")
#         raise AuthenticationFailed('Invalid authentication tokens.')

#     def process_response(self, request, response):
#         # Add the refreshed token in the response
#         if hasattr(request, 'auth') and isinstance(request.auth, str):
#             response.set_cookie(
#                 key='token',
#                 value=request.auth,
#                 httponly=True,
#                 secure=True,
#                 samesite='None',
#                 path="/",
#                 max_age=2 * 60  # 15 minutes
#             )
#         return response
