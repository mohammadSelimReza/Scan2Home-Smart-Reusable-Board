from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'property', 'property_title', 'buyer_name',
            'date', 'time_slot', 'message', 'status', 'created_at'
        )
        read_only_fields = ('id', 'status', 'created_at', 'buyer_name')

    def create(self, validated_data):
        validated_data['buyer'] = self.context['request'].user
        return super().create(validated_data)
