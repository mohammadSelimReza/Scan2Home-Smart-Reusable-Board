from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.AgentRegisterView.as_view(), name='agent-register'),
    path('login/', views.LoginView.as_view(), name='agent-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='agent-token-refresh'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='agent-forgot-password'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='agent-verify-otp'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='agent-reset-password'),
    path('profile/', views.ProfileView.as_view(), name='agent-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='agent-change-password'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='agent-delete-account'),
]
