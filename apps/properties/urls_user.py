from django.urls import path
from . import views

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='user-property-list'),
    path('<uuid:pk>/', views.PropertyDetailView.as_view(), name='user-property-detail'),
    path('<uuid:pk>/favourite/', views.FavouriteToggleView.as_view(), name='user-property-favourite'),
    path('favourites/', views.FavouriteListView.as_view(), name='user-favourite-list'),
    path('<uuid:pk>/similar/', views.SimilarPropertyView.as_view(), name='user-similar-properties'),
    path('support/', views.UserSupportMessageView.as_view(), name='user-support-message'),
]
