from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .authentication import generate_token
from .serializers import (
    RegisterSerializer, LoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer,
)

# ── Reusable response schemas ────────────────────────────────────────────────

_TOKEN_RESPONSE = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "token":      openapi.Schema(type=openapi.TYPE_STRING, example="eyJhbGci..."),
        "token_type": openapi.Schema(type=openapi.TYPE_STRING, example="Bearer"),
        "expires_in": openapi.Schema(type=openapi.TYPE_INTEGER, example=86400),
        "user": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id":          openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "username":    openapi.Schema(type=openapi.TYPE_STRING,  example="johndoe"),
                "email":       openapi.Schema(type=openapi.TYPE_STRING,  example="john@example.com"),
                "first_name":  openapi.Schema(type=openapi.TYPE_STRING,  example="John"),
                "last_name":   openapi.Schema(type=openapi.TYPE_STRING,  example="Doe"),
                "date_joined": openapi.Schema(type=openapi.TYPE_STRING,  example="2025-01-01T00:00:00Z"),
            },
        ),
    },
)

_401 = openapi.Response(
    "Unauthorized",
    openapi.Schema(type=openapi.TYPE_OBJECT,
                   properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)}),
)
_400 = openapi.Response(
    "Validation Error",
    openapi.Schema(type=openapi.TYPE_OBJECT,
                   properties={"field": openapi.Schema(type=openapi.TYPE_ARRAY,
                               items=openapi.Schema(type=openapi.TYPE_STRING))}),
)


# ── Views ────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Register a new user",
        operation_description=(
            "Create a new account. Returns a **JWT token** you can use immediately.\n\n"
            "**No auth required.**"
        ),
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response("User created — JWT token returned", _TOKEN_RESPONSE),
            400: _400,
            409: openapi.Response("Username or email already taken",
                                  openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={"error": openapi.Schema(type=openapi.TYPE_STRING)})),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        token = generate_token(user)
        return Response({
            "token": token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_EXPIRY_HOURS * 3600,
            "user": UserProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Login — get a JWT token",
        operation_description=(
            "Authenticate with your credentials. Copy the `token` from the response, "
            "then click **Authorize 🔒** at the top and enter `Bearer <token>`.\n\n"
            "**No auth required.**"
        ),
        request_body=LoginSerializer,
        responses={
            200: openapi.Response("Login successful", _TOKEN_RESPONSE),
            400: _400,
            401: openapi.Response("Invalid credentials",
                                  openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={"error": openapi.Schema(type=openapi.TYPE_STRING,
                                                             example="Invalid username or password.")})),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
        token = generate_token(user)
        return Response({
            "token": token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_EXPIRY_HOURS * 3600,
            "user": UserProfileSerializer(user).data,
        })


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Logout",
        operation_description=(
            "Signals the client to discard the token. JWTs are stateless — "
            "invalidation is handled on the client side."
        ),
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={
            200: openapi.Response("Logged out",
                                  openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={"message": openapi.Schema(type=openapi.TYPE_STRING)})),
        },
    )
    def post(self, request):
        return Response({"message": "Logged out successfully. Please discard your token."})


class VerifyTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_summary="Verify token",
        operation_description="Check if your Bearer token is valid. 🔒 **Requires auth.**",
        responses={
            200: openapi.Response("Token valid",
                                  openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={
                                                     "valid": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                                     "user":  openapi.Schema(type=openapi.TYPE_OBJECT),
                                                 })),
            401: _401,
        },
        security=[{"Bearer": []}],
    )
    def get(self, request):
        return Response({"valid": True, "user": UserProfileSerializer(request.user).data})


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["User"],
        operation_summary="Get my profile",
        operation_description="Returns the authenticated user's profile. 🔒 **Requires auth.**",
        responses={200: openapi.Response("Profile", UserProfileSerializer), 401: _401},
        security=[{"Bearer": []}],
    )
    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    @swagger_auto_schema(
        tags=["User"],
        operation_summary="Update my profile",
        operation_description="Update `email`, `first_name`, or `last_name`. 🔒 **Requires auth.**",
        request_body=UserProfileSerializer,
        responses={200: openapi.Response("Updated profile", UserProfileSerializer), 400: _400, 401: _401},
        security=[{"Bearer": []}],
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["User"],
        operation_summary="Change password",
        operation_description=(
            "Change your password. A **new token** is issued — use it going forward.\n\n"
            "🔒 **Requires auth.**"
        ),
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response("Password changed — new token issued", _TOKEN_RESPONSE),
            400: _400,
            401: openapi.Response("Wrong current password / Unauthorized",
                                  openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties={"error": openapi.Schema(type=openapi.TYPE_STRING)})),
        },
        security=[{"Bearer": []}],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.check_password(serializer.validated_data["old_password"]):
            return Response({"error": "Current password is incorrect."}, status=status.HTTP_401_UNAUTHORIZED)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        token = generate_token(request.user)
        return Response({
            "token": token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_EXPIRY_HOURS * 3600,
            "user": UserProfileSerializer(request.user).data,
        })
