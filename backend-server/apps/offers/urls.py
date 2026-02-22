from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubmitOfferView.as_view(), name='offer-submit'),
    path('agent/', views.AgentOfferListView.as_view(), name='agent-offer-list'),
    path('<uuid:offer_id>/history/', views.OfferHistoryView.as_view(), name='offer-history'),
    path('<uuid:offer_id>/counter/', views.CounterOfferView.as_view(), name='offer-counter'),
    path('<uuid:offer_id>/<str:action>/', views.AgentOfferActionView.as_view(), name='offer-action'),
]
