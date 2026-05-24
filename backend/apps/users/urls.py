from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RequestOTPView,
    VerifyOTPView,
    ResendOTPView,
    UserProfileView,
    UserOnboardingView,
    AddressListCreateView,
    AddressDetailView,
    SetDefaultAddressView,
)

urlpatterns = [
    # Auth endpoints
    path('auth/otp/request/', RequestOTPView.as_view(), name='request-otp'),
    path('auth/otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/otp/resend/', ResendOTPView.as_view(), name='resend-otp'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User profile endpoints
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('users/onboarding/', UserOnboardingView.as_view(), name='user-onboarding'),
    
    # Address endpoints
    path('users/addresses/', AddressListCreateView.as_view(), name='address-list'),
    path('users/addresses/<uuid:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('users/addresses/<uuid:pk>/set-default/', SetDefaultAddressView.as_view(), name='address-set-default'),
]
