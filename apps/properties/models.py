import uuid
from django.db import models
from django.conf import settings


class PropertyType(models.TextChoices):
    HOUSE = 'house', 'House'
    APARTMENT = 'apartment', 'Apartment'
    VILLA = 'villa', 'Villa'


class PropertyStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    UNDER_OFFER = 'under_offer', 'Under Offer'
    SOLD = 'sold', 'Sold'


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='properties', limit_choices_to={'role': 'agent'}
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, default=PropertyType.HOUSE)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    address = models.CharField(max_length=512)
    postcode = models.CharField(max_length=20, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=PropertyStatus.choices, default=PropertyStatus.AVAILABLE)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # admin approval

    # Key Features
    beds = models.PositiveSmallIntegerField(default=0)
    baths = models.PositiveSmallIntegerField(default=0)
    size_sqft = models.PositiveIntegerField(default=0)
    parking_slots = models.PositiveSmallIntegerField(default=0)
    has_pool = models.BooleanField(default=False)
    has_garage = models.BooleanField(default=False)
    has_garden = models.BooleanField(default=False)
    has_fireplace = models.BooleanField(default=False)
    is_smart_home = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    is_pet_friendly = models.BooleanField(default=False)

    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_type']),
            models.Index(fields=['status']),
            models.Index(fields=['price']),
            models.Index(fields=['agent']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_new(self):
        from django.utils import timezone
        from datetime import timedelta
        return (timezone.now() - self.created_at).days <= 7


class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_images'
        ordering = ['order']


class PropertyVideo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='video')
    video_file = models.FileField(upload_to='property_videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_videos'


class PropertyFavourite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favourites'
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favourited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'property_favourites'
        unique_together = ('user', 'property')


class SupportMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_messages')
    message = models.TextField()
    reply = models.TextField(blank=True)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'support_messages'
        ordering = ['-created_at']


class StaticPage(models.Model):
    class PageType(models.TextChoices):
        TERMS = 'terms', 'Terms & Conditions'
        PRIVACY = 'privacy', 'Privacy Policy'

    page_type = models.CharField(max_length=20, choices=PageType.choices, unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'static_pages'

    def __str__(self):
        return self.page_type


class PropertyType2(models.Model):
    """Admin-configurable property type labels (e.g. house, apartment, villa, studio...)"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'property_types_config'

    def __str__(self):
        return self.name
