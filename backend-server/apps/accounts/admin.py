from django.contrib import admin
from .models import CustomUser, AgentProfile, OTPVerification, AgentReview


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_banned', 'member_since')
    list_filter = ('role', 'is_active', 'is_banned')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('-member_since',)


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand_name', 'is_verified', 'rating')
    list_filter = ('is_verified',)
    search_fields = ('brand_name', 'user__email')


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'created_at', 'expires_at', 'is_used')
    search_fields = ('email', 'otp_code')


@admin.register(AgentReview)
class AgentReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'agent__brand_name')
