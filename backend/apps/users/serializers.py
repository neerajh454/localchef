from rest_framework import serializers
from .models import User, Address, OTP


class RequestOTPSerializer(serializers.Serializer):
    """Serializer for requesting OTP."""
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        # Remove any spaces or special characters
        cleaned = ''.join(filter(str.isdigit, value))
        if len(cleaned) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return cleaned


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP."""
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)

    def validate_phone_number(self, value):
        cleaned = ''.join(filter(str.isdigit, value))
        if len(cleaned) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return cleaned

    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("OTP must be 6 digits")
        return value


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP."""
    phone_number = serializers.CharField(max_length=15)
    retry_type = serializers.ChoiceField(
        choices=['text', 'voice'],
        default='text',
        help_text="Retry type: 'text' for SMS, 'voice' for voice call"
    )

    def validate_phone_number(self, value):
        cleaned = ''.join(filter(str.isdigit, value))
        if len(cleaned) < 10:
            raise serializers.ValidationError("Invalid phone number")
        return cleaned


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'name', 'profile_image', 
            'role', 'is_phone_verified', 'created_at'
        ]
        read_only_fields = ['id', 'phone_number', 'is_phone_verified', 'created_at']


class UserOnboardingSerializer(serializers.ModelSerializer):
    """Serializer for completing user profile (first-time users)."""

    class Meta:
        model = User
        fields = ['name', 'role']

    def validate_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters")
        return value.strip()


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model."""

    class Meta:
        model = Address
        fields = [
            'id', 'label', 'address_line', 'landmark', 
            'city', 'state', 'pincode', 'latitude', 
            'longitude', 'is_default', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AddressCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating address during onboarding."""

    class Meta:
        model = Address
        fields = [
            'label', 'address_line', 'landmark', 
            'city', 'state', 'pincode', 'latitude', 'longitude'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        # First address is default
        is_first = not Address.objects.filter(user=user).exists()
        return Address.objects.create(
            user=user,
            is_default=is_first,
            **validated_data
        )


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    is_new_user = serializers.BooleanField()
    user = UserSerializer()
