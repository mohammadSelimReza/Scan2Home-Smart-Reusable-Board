from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'property', 'date', 'time_slot', 'status', 'created_at')
    list_filter = ('status',)
