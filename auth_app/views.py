from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .authentication import generate_token
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    TokenResponseSerializer,
    MessageSerializer,
)


# ─────────────────────────────────────────────
#  Shared Swagger response schemas
# ─────────────────────────────────────────────
_error_401 = openapi.Response(
    description='Unauthorized – missing or invalid token.',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'detail': openapi.Schema(type=openapi.TYPE_STRING, example='Authentication credentials were not provided.')
        },
    ),
)
_error_400 = openapi.Response(
    description='Bad Request – validation errors.',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'field_name': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=['This field is required.'],
            )
        },
    ),
)


# ─────────────────────────────────────────────
#  Register
# ─────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id='auth_register',
        operation_summary='Register a new user',
        operation_description=(
            'Create a new user account by providing a unique username, a valid email, '
            'and a strong password (minimum 8 characters, not entirely numeric).\n\n'
            '**No authentication required.**'
        ),
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(description='User created successfully.', schema=TokenResponseSerializer),
            400: _error_400,
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_token(user)
            return Response(
                {
                    'token': token,
                    'token_type': 'Bearer',
                    'expires_in': settings.JWT_EXPIRY_HOURS * 3600,
                    'user': UserProfileSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Login
# ─────────────────────────────────────────────
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id='auth_login',
        operation_summary='Login and obtain JWT token',
        operation_description=(
            'Authenticate with your username and password to receive a **JWT Bearer token**.\n\n'
            'Copy the returned `token` value and click **Authorize** (🔒 button at the top), '
            'then enter `Bearer <token>`.\n\n'
            '**No authentication required.**'
        ),
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(description='Login successful.', schema=TokenResponseSerializer),
            400: _error_400,
            401: openapi.Response(
                description='Invalid credentials.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, example='Invalid username or password.')},
                ),
            ),
        },
        tags=['Authentication'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
            )
            if user:
                token = generate_token(user)
                return Response(
                    {
                        'token': token,
                        'token_type': 'Bearer',
                        'expires_in': settings.JWT_EXPIRY_HOURS * 3600,
                        'user': UserProfileSerializer(user).data,
                    }
                )
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Logout
# ─────────────────────────────────────────────
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='auth_logout',
        operation_summary='Logout (invalidate session)',
        operation_description=(
            'Signals the client to discard the JWT token.\n\n'
            '> **Note:** JWTs are stateless; true server-side invalidation requires a token blacklist. '
            'This endpoint is a best-practice placeholder.\n\n'
            '**🔒 Requires Bearer token.**'
        ),
        responses={
            200: openapi.Response(description='Logged out successfully.', schema=MessageSerializer),
            401: _error_401,
        },
        tags=['Authentication'],
        security=[{'Bearer': []}],
    )
    def post(self, request):
        return Response({'message': 'Successfully logged out.', 'detail': 'Please discard your token on the client side.'})


# ─────────────────────────────────────────────
#  Profile
# ─────────────────────────────────────────────
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='auth_profile_read',
        operation_summary='Get current user profile',
        operation_description='Returns the authenticated user\'s profile details.\n\n**🔒 Requires Bearer token.**',
        responses={
            200: openapi.Response(description='User profile.', schema=UserProfileSerializer),
            401: _error_401,
        },
        tags=['User'],
        security=[{'Bearer': []}],
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_id='auth_profile_update',
        operation_summary='Update user profile',
        operation_description=(
            'Update editable profile fields: `email`, `first_name`, `last_name`.\n\n'
            '**🔒 Requires Bearer token.**'
        ),
        request_body=UserProfileSerializer,
        responses={
            200: openapi.Response(description='Profile updated.', schema=UserProfileSerializer),
            400: _error_400,
            401: _error_401,
        },
        tags=['User'],
        security=[{'Bearer': []}],
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Change Password
# ─────────────────────────────────────────────
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='auth_change_password',
        operation_summary='Change user password',
        operation_description=(
            'Change the authenticated user\'s password by providing the current password and a new one.\n\n'
            '**🔒 Requires Bearer token.**'
        ),
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(description='Password changed. A new token is issued.', schema=TokenResponseSerializer),
            400: _error_400,
            401: openapi.Response(
                description='Old password is incorrect.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING, example='Old password is incorrect.')},
                ),
            ),
        },
        tags=['User'],
        security=[{'Bearer': []}],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            token = generate_token(request.user)
            return Response(
                {
                    'token': token,
                    'token_type': 'Bearer',
                    'expires_in': settings.JWT_EXPIRY_HOURS * 3600,
                    'user': UserProfileSerializer(request.user).data,
                    'message': 'Password changed successfully.',
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
#  Token Verify
# ─────────────────────────────────────────────
class VerifyTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id='auth_verify_token',
        operation_summary='Verify JWT token validity',
        operation_description=(
            'Returns the current user\'s info if the supplied token is valid and not expired.\n\n'
            '**🔒 Requires Bearer token.**'
        ),
        responses={
            200: openapi.Response(
                description='Token is valid.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'valid': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            401: _error_401,
        },
        tags=['Authentication'],
        security=[{'Bearer': []}],
    )
    def get(self, request):
        return Response({'valid': True, 'user': UserProfileSerializer(request.user).data})
