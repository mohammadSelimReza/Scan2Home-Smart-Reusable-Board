from rest_framework import serializers
from apps.properties.models import SupportMessage, PropertyType2
from apps.properties.serializers import PropertyListSerializer
from apps.accounts.serializers import UserProfileSerializer
class AdminActivitySerializer(serializers.Serializer):
    id = serializers.CharField()
    user = UserProfileSerializer()
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()
    details = serializers.CharField()

class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_agents = serializers.IntegerField()
    total_agents_verified = serializers.IntegerField()
    total_agents_pending = serializers.IntegerField()
    total_properties = serializers.IntegerField()
    total_properties_approved = serializers.IntegerField()
    total_properties_pending = serializers.IntegerField()
    total_views_counts = serializers.IntegerField()
    property_by_type = serializers.DictField()
    latest_requested_properties = PropertyListSerializer(many=True)
    recent_user_activities = AdminActivitySerializer(many=True)

class AdminActionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class PropertyTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='name')
    class Meta:
        model = PropertyType2
        fields = ('id', 'type')

class AdminSupportMessageSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.full_name')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = SupportMessage
        fields = ('id', 'user', 'email', 'message', 'reply', 'is_replied', 'created_at', 'replied_at')

class SupportReplySerializer(serializers.Serializer):
    message = serializers.CharField()
