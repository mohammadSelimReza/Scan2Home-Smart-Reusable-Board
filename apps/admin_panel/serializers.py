from rest_framework import serializers
from apps.properties.models import SupportMessage, PropertyType2

class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_agents = serializers.IntegerField()
    total_agents_verified = serializers.IntegerField()
    total_agents_pending = serializers.IntegerField()
    total_properties = serializers.IntegerField()
    total_properties_approved = serializers.IntegerField()
    total_properties_pending = serializers.IntegerField()
    property_by_type = serializers.DictField()

class AdminActionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType2
        fields = ('name', 'slug')

class AdminSupportMessageSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.full_name')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = SupportMessage
        fields = ('id', 'user', 'email', 'message', 'reply', 'is_replied', 'created_at', 'replied_at')

class SupportReplySerializer(serializers.Serializer):
    reply = serializers.CharField()
