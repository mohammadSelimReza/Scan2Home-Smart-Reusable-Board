from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingCreateView.as_view(), name='user-booking-create'),
    path('my/', views.MyBookingsView.as_view(), name='user-my-bookings'),
]
