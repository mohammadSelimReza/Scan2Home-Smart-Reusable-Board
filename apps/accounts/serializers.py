from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AgentProfile

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

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'phone', 'role',
            'profile_picture', 'is_2fa_enabled', 'member_since',
            'agent_profile'
        )
        read_only_fields = ('id', 'email', 'role', 'member_since')


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
    otp_code = serializers.CharField(max_length=6, min_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)


# ── Notification settings ────────────────────────────────────

class NotificationSettingsSerializer(serializers.Serializer):
    push_enabled = serializers.BooleanField()
    email_enabled = serializers.BooleanField()
