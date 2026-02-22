from django.urls import path
from . import views

# Public QR redirect endpoint
urlpatterns = [
    path('<uuid:qr_id>/', views.QRScanRedirectView.as_view(), name='qr-scan-redirect'),
]
