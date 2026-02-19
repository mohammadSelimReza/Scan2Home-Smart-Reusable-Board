from rest_framework import serializers
from .models import Offer, CounterOffer


class CounterOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounterOffer
        fields = ('id', 'by_agent', 'amount', 'message', 'created_at')
        read_only_fields = ('id', 'by_agent', 'created_at')


class OfferSerializer(serializers.ModelSerializer):
    counter_offers = CounterOfferSerializer(many=True, read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = Offer
        fields = (
            'id', 'property', 'property_title', 'buyer_name', 'email', 'phone',
            'offer_amount', 'message', 'status', 'is_lead',
            'counter_offers', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'is_lead', 'created_at', 'updated_at')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['buyer'] = request.user
        return super().create(validated_data)


class CounterOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounterOffer
        fields = ('amount', 'message')
