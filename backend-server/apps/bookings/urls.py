from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookingCreateView.as_view(), name='booking-create'),
    path('my/', views.MyBookingsView.as_view(), name='my-bookings'),
    path('agent/', views.AgentBookingsView.as_view(), name='agent-bookings'),
    path('<uuid:pk>/<str:action>/', views.BookingActionView.as_view(), name='booking-action'),
]
