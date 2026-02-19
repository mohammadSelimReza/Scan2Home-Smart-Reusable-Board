from rest_framework import serializers
from .models import Property, PropertyImage, PropertyVideo, PropertyFavourite, SupportMessage
from apps.accounts.serializers import AgentProfileSerializer


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

    class Meta:
        model = Property
        fields = (
            'id', 'title', 'property_type', 'price', 'address', 'postcode',
            'status', 'is_featured', 'is_new', 'beds', 'baths', 'size_sqft',
            'lat', 'lon', 'cover_image', 'views_count', 'is_favourited', 'created_at'
        )

    def get_cover_image(self, obj):
        img = obj.images.filter(is_cover=True).first() or obj.images.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None

    def get_is_favourited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favourited_by.filter(user=request.user).exists()
        return False


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    video = PropertyVideoSerializer(read_only=True)
    agent = AgentMinimalSerializer(read_only=True)
    is_new = serializers.BooleanField(read_only=True)
    is_favourited = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

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
