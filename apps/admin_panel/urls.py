from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),

    # Property management
    path('properties/', views.AdminPropertyListView.as_view(), name='admin-property-list'),
    path('properties/<uuid:pk>/<str:action>/', views.AdminPropertyActionView.as_view(), name='admin-property-action'),

    # User management
    path('users/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<uuid:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('users/<uuid:pk>/ban/', views.AdminUserDetailView.as_view(), name='admin-user-ban'),

    # Agent management
    path('agents/', views.AdminAgentListView.as_view(), name='admin-agent-list'),
    path('agents/<uuid:pk>/verify/', views.AdminAgentVerifyView.as_view(), name='admin-agent-verify'),
    path('agents/<uuid:pk>/ban/', views.AdminAgentBanView.as_view(), name='admin-agent-ban'),

    # Static pages (admin editable)
    path('settings/terms/', views.StaticPageView.as_view(), {'page_type': 'terms'}, name='admin-terms'),
    path('settings/privacy/', views.StaticPageView.as_view(), {'page_type': 'privacy'}, name='admin-privacy'),

    # Property types config
    path('settings/property-types/', views.PropertyTypeConfigView.as_view(), name='admin-property-types'),

    # Support messages
    path('support/', views.SupportMessageListView.as_view(), name='admin-support-list'),
    path('support/<uuid:pk>/reply/', views.SupportMessageReplyView.as_view(), name='admin-support-reply'),
]

# Public pages (terms / privacy for buyers)
from django.urls import include
public_urlpatterns = [
    path('pages/<str:page_type>/', views.PublicStaticPageView.as_view(), name='public-static-page'),
]
