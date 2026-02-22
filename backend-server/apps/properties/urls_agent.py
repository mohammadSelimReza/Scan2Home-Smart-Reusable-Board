from django.urls import path
from . import views

urlpatterns = [
    path('', views.AgentPropertyListView.as_view(), name='agent-property-list'),
    path('create/', views.PropertyCreateView.as_view(), name='agent-property-create'),
    path('<uuid:pk>/', views.PropertyDetailView.as_view(), name='agent-property-detail'), # Detail view for agent as well
    path('<uuid:pk>/images/', views.PropertyImageUploadView.as_view(), name='agent-property-image-upload'),
    path('<uuid:pk>/video/', views.PropertyVideoUploadView.as_view(), name='agent-property-video-upload'),
]
