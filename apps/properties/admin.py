from django.contrib import admin
from .models import Property, PropertyImage, PropertyVideo, PropertyFavourite, SupportMessage, StaticPage, PropertyType2


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'status', 'is_approved', 'is_featured', 'price', 'agent', 'created_at')
    list_filter = ('property_type', 'status', 'is_approved', 'is_featured')
    search_fields = ('title', 'address', 'postcode')
    ordering = ('-created_at',)


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'is_cover', 'order')


@admin.register(PropertyVideo)
class PropertyVideoAdmin(admin.ModelAdmin):
    list_display = ('property', 'uploaded_at')


@admin.register(PropertyFavourite)
class PropertyFavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'added_at')


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_replied', 'created_at', 'replied_at')
    list_filter = ('is_replied',)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('page_type', 'updated_at')


@admin.register(PropertyType2)
class PropertyType2Admin(admin.ModelAdmin):
    list_display = ('name', 'slug')
