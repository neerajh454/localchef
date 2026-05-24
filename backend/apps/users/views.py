from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .models import User, Address, OTP
from .serializers import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    UserSerializer,
    UserOnboardingSerializer,
    AddressSerializer,
    AddressCreateSerializer,
)


class RequestOTPView(APIView):
    """Request OTP for phone number verification."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        
        # TODO: Integrate MSG91 Send OTP API
        # API: POST https://control.msg91.com/api/v5/otp
        # For now, using fixed OTP for testing
        
        return Response({
            'message': 'OTP sent successfully',
            'phone_number': phone_number,
            'type': 'success',
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """Verify OTP and return JWT tokens."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp']
        
        # TODO: Integrate MSG91 Verify OTP API
        # API: GET https://control.msg91.com/api/v5/otp/verify?otp=&mobile=
        # For now, using fixed OTP for testing
        dev_otp = getattr(settings, 'DEV_OTP_CODE', '123456')
        
        if otp_code != dev_otp:
            return Response({
                'error': 'Invalid or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user
        user, created = User.objects.get_or_create(phone_number=phone_number)
        user.is_phone_verified = True
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Check if user needs onboarding (no name set)
        is_new_user = not user.name
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'is_new_user': is_new_user,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """Resend OTP to phone number (via SMS or voice call)."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        retry_type = serializer.validated_data['retry_type']
        
        # TODO: Integrate MSG91 Resend OTP API
        # API: GET https://control.msg91.com/api/v5/otp/retry?authkey=&retrytype=&mobile=
        # For now, using fixed OTP for testing
        
        return Response({
            'message': f'OTP resent successfully via {retry_type}',
            'phone_number': phone_number,
            'retry_type': retry_type,
            'type': 'success',
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user's profile."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserOnboardingView(APIView):
    """Complete user profile after first login."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserOnboardingSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data,
        }, status=status.HTTP_200_OK)


class AddressListCreateView(generics.ListCreateAPIView):
    """List user's addresses or create new one."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddressCreateSerializer
        return AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific address."""
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class SetDefaultAddressView(APIView):
    """Set an address as default."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
            address.is_default = True
            address.save()
            return Response({
                'message': 'Default address updated',
                'address': AddressSerializer(address).data
            })
        except Address.DoesNotExist:
            return Response({
                'error': 'Address not found'
            }, status=status.HTTP_404_NOT_FOUND)
