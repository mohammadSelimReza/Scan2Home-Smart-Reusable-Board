from django.contrib import admin
from .models import Offer, CounterOffer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'property', 'offer_amount', 'status', 'is_lead', 'created_at')
    list_filter = ('status', 'is_lead')
    search_fields = ('buyer_name', 'email')


@admin.register(CounterOffer)
class CounterOfferAdmin(admin.ModelAdmin):
    list_display = ('offer', 'by_agent', 'amount', 'created_at')
