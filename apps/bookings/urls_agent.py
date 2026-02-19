from django.urls import path
from . import views

urlpatterns = [
    path('', views.AgentBookingsView.as_view(), name='agent-bookings-list'),
    path('<uuid:pk>/<str:action>/', views.BookingActionView.as_view(), name='agent-booking-action'),
]
