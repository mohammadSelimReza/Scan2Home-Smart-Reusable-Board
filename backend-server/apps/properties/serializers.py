from rest_framework import serializers
from .models import Property, PropertyImage, PropertyVideo, PropertyFavourite, SupportMessage
from apps.accounts.serializers import AgentProfileSerializer
from drf_spectacular.utils import extend_schema_field


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ('id', 'image', 'is_cover', 'order')


class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ('id', 'video_file', 'uploaded_at')


class AgentMinimalSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    agent_profile = AgentProfileSerializer()


class PropertyListSerializer(serializers.ModelSerializer):
    cover_image = serializers.SerializerMethodField()
    is_new = serializers.BooleanField(read_only=True)
    is_favourited = serializers.SerializerMethodField()
    agent_id = serializers.UUIDField(source='agent.id', read_only=True)

    class Meta:
        model = Property
        fields = (
            'id', 'title', 'property_type', 'price', 'address', 'postcode',
            'status', 'is_featured', 'is_new', 'beds', 'baths', 'size_sqft',
            'lat', 'lon', 'cover_image', 'views_count', 'is_favourited', 'created_at',
            'agent_id'
        )

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_cover_image(self, obj):
        img = obj.images.filter(is_cover=True).first() or obj.images.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None

    @extend_schema_field(serializers.BooleanField())
    def get_is_favourited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favourited_by.filter(user=request.user).exists()
        return False


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    video = PropertyVideoSerializer(read_only=True)
    agent = AgentMinimalSerializer(read_only=True)
    agent_id = serializers.UUIDField(source='agent.id', read_only=True)
    is_new = serializers.BooleanField(read_only=True)
    is_favourited = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    @extend_schema_field(serializers.BooleanField())
    def get_is_favourited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favourited_by.filter(user=request.user).exists()
        return False


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        exclude = ('agent', 'views_count', 'is_approved', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['agent'] = self.context['request'].user
        return super().create(validated_data)


class PropertyImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ('image', 'is_cover', 'order')


class PropertyVideoUploadSerializer(serializers.Serializer):
    video_file = serializers.FileField()


class FavouriteSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)

    class Meta:
        model = PropertyFavourite
        fields = ('id', 'property', 'added_at')


class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ('message',)


class AdminPropertySerializer(PropertyListSerializer):
    created_by = serializers.CharField(source='agent.full_name', read_only=True)
    total_view_count = serializers.IntegerField(source='views_count', read_only=True)
    total_offer_got_count = serializers.SerializerMethodField()
    total_qr_scanned_count = serializers.IntegerField(source='qr_scanned_count', read_only=True)

    class Meta(PropertyListSerializer.Meta):
        fields = PropertyListSerializer.Meta.fields + (
            'created_by', 'total_view_count', 'total_offer_got_count',
            'total_qr_scanned_count'
        )

    @extend_schema_field(serializers.IntegerField())
    def get_total_offer_got_count(self, obj):
        return obj.offers.count()


class AdminPropertyDetailSerializer(PropertyDetailSerializer):
    created_by = serializers.CharField(source='agent.full_name', read_only=True)
    total_view_count = serializers.IntegerField(source='views_count', read_only=True)
    total_offer_got_count = serializers.SerializerMethodField()
    total_qr_scanned_count = serializers.IntegerField(source='qr_scanned_count', read_only=True)

    class Meta:
        model = Property
        fields = '__all__'
        # We don't need to add them to fields if we use __all__ and they are defined on the class?
        # Actually DRF includes declared fields even with __all__. 
        # But to be safe and clean, I'll list the ones I want to add if I really need to, 
        # but let's see: declaring them as fields on the class usually includes them.
    
    @extend_schema_field(serializers.IntegerField())
    def get_total_offer_got_count(self, obj):
        return obj.offers.count()
