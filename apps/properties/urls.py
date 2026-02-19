from django.urls import path
from . import views

urlpatterns = [
    # Public & Filter
    path('', views.PropertyListView.as_view(), name='property-list'),
    path('create/', views.PropertyCreateView.as_view(), name='property-create'),
    path('<uuid:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),
    
    # Media
    path('<uuid:pk>/images/', views.PropertyImageUploadView.as_view(), name='property-image-upload'),
    path('<uuid:pk>/video/', views.PropertyVideoUploadView.as_view(), name='property-video-upload'),

    # Favourites
    path('<uuid:pk>/favourite/', views.FavouriteToggleView.as_view(), name='property-favourite'),
    path('favourites/', views.FavouriteListView.as_view(), name='favourite-list'),

    # Agent
    path('my/', views.AgentPropertyListView.as_view(), name='agent-property-list'),

    # Similar
    path('<uuid:pk>/similar/', views.SimilarPropertyView.as_view(), name='similar-properties'),

    # Support
    path('support/', views.UserSupportMessageView.as_view(), name='user-support-message'),
]
