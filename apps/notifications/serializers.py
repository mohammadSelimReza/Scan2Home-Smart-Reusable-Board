from rest_framework import serializers
from .models import Notification, UserNotificationSettings


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'body', 'notification_type', 'is_read', 'created_at')
        read_only_fields = fields


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSettings
        fields = ('push_enabled', 'email_enabled')
