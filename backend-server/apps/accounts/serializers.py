from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.timesince import timesince
from django.db.models import Sum
from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from .models import AgentProfile, AgentReview

User = get_user_model()


# ── Registration ────────────────────────────────────────────

class BuyerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'password')

    def create(self, validated_data):
        return User.objects.create_user(role='buyer', **validated_data)


class AgentRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    brand_name = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone', 'password', 'brand_name', 'website')

    def create(self, validated_data):
        brand_name = validated_data.pop('brand_name', '')
        website = validated_data.pop('website', '')
        user = User.objects.create_user(role='agent', **validated_data)
        AgentProfile.objects.create(user=user, brand_name=brand_name, website=website)
        return user


# ── Profile ─────────────────────────────────────────────────

class AgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentProfile
        fields = (
            'brand_name', 'logo', 'brand_color', 'website',
            'agent_photo', 'is_verified', 'rating', 'rating_count'
        )
        read_only_fields = ('is_verified', 'rating', 'rating_count')


class UserProfileSerializer(serializers.ModelSerializer):
    agent_profile = AgentProfileSerializer(read_only=True)
    last_active_human = serializers.SerializerMethodField()
    account_status = serializers.SerializerMethodField()
    total_properties_count = serializers.SerializerMethodField()
    total_views_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'phone', 'role',
            'profile_picture', 'is_2fa_enabled', 'member_since',
            'last_active', 'last_active_human', 'account_status',
            'total_properties_count', 'total_views_count',
            'agent_profile'
        )
        read_only_fields = ('id', 'email', 'role', 'member_since', 'last_active')

    @extend_schema_field(OpenApiTypes.STR)
    def get_last_active_human(self, obj):
        if not obj.last_active:
            return "Never"
        return f"{timesince(obj.last_active).split(',')[0]} ago"

    @extend_schema_field(OpenApiTypes.STR)
    def get_account_status(self, obj):
        if obj.is_banned:
            return "suspend"
        if not obj.is_active:
            return "inactive"
        return "active"

    @extend_schema_field(OpenApiTypes.INT)
    def get_total_properties_count(self, obj):
        if obj.role != 'agent':
            return 0
        return obj.properties.count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_total_views_count(self, obj):
        if obj.role != 'agent':
            return 0
        return obj.properties.aggregate(Sum('views_count'))['views_count__sum'] or 0


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    agent_profile = AgentProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ('full_name', 'phone', 'profile_picture', 'is_2fa_enabled', 'agent_profile')

    def update(self, instance, validated_data):
        agent_data = validated_data.pop('agent_profile', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if agent_data and hasattr(instance, 'agent_profile'):
            agent_profile = instance.agent_profile
            for attr, val in agent_data.items():
                setattr(agent_profile, attr, val)
            agent_profile.save()
        return instance


# ── Auth & Password ─────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=4, min_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=4, min_length=4)
    new_password = serializers.CharField(write_only=True, min_length=8)


# ── Notification settings ────────────────────────────────────

class NotificationSettingsSerializer(serializers.Serializer):
    push_enabled = serializers.BooleanField()
    email_enabled = serializers.BooleanField()


# ── Agent Review ──────────────────────────────────────────────

class AgentReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_avatar = serializers.ImageField(source='user.profile_picture', read_only=True)

    class Meta:
        model = AgentReview
        fields = ('id', 'user_name', 'user_avatar', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'created_at')
