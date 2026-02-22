from rest_framework import serializers

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)

class ChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    fallback = serializers.BooleanField(required=False, default=False)
