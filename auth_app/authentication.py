import jwt
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


def generate_token(user):
    """Generate a JWT token for a user."""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=settings.JWT_EXPIRY_HOURS),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token):
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired. Please login again.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token. Please login again.')


class JWTAuthentication(BaseAuthentication):
    """Custom JWT authentication class for DRF."""

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            payload = decode_token(token)
            user = User.objects.get(id=payload['user_id'])
            return (user, token)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
