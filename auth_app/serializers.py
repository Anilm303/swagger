from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Must be at least 8 characters.',
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password',
        help_text='Enter the same password again for verification.',
    )
    email = serializers.EmailField(required=True, help_text='A valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text='Your registered username.')
    password = serializers.CharField(
        style={'input_type': 'password'},
        help_text='Your account password.',
    )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text='Your current password.',
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text='Your new password (min 8 characters).',
    )
    new_password2 = serializers.CharField(
        style={'input_type': 'password'},
        label='Confirm New Password',
        help_text='Enter the new password again.',
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'New passwords do not match.'})
        validate_password(attrs['new_password'])
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField(help_text='JWT Bearer token. Use as: Authorization: Bearer <token>')
    token_type = serializers.CharField(default='Bearer')
    expires_in = serializers.IntegerField(help_text='Token validity in seconds.')
    user = UserProfileSerializer()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    detail = serializers.CharField(required=False)
