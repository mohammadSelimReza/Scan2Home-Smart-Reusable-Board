from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubmitOfferView.as_view(), name='user-offer-submit'),
    path('<uuid:offer_id>/history/', views.OfferHistoryView.as_view(), name='user-offer-history'),
]
