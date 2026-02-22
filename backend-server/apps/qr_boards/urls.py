from django.urls import path
from . import views

urlpatterns = [
    path('', views.QRBoardListCreateView.as_view(), name='qr-board-list'),
    path('<uuid:qr_id>/', views.QRBoardDetailView.as_view(), name='qr-board-detail'),
    path('<uuid:qr_id>/reassign/', views.QRBoardReassignView.as_view(), name='qr-board-reassign'),
    path('<uuid:qr_id>/download-qr/', views.QRBoardDownloadView.as_view(), name='qr-board-download'),
]
