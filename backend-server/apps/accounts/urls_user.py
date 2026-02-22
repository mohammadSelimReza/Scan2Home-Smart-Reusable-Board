from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.BuyerRegisterView.as_view(), name='user-register'),
    path('login/', views.LoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='user-token-refresh'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='user-forgot-password'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='user-verify-otp'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='user-reset-password'),
    path('profile/', views.ProfileView.as_view(), name='user-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='user-change-password'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='user-delete-account'),
]
