from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API v1
    # ── User (Buyer) Scope ──────────────────────────────────────────
    path('api/v1/user/', include([
        path('auth/', include('apps.accounts.urls_user')),
        path('properties/', include('apps.properties.urls_user')),
        path('bookings/', include('apps.bookings.urls_user')),
        path('offers/', include('apps.offers.urls_user')),
        path('notifications/', include('apps.notifications.urls_role')),
        path('chat/', include('apps.chat.urls')),
    ])),

    # ── Agent (Seller) Scope ─────────────────────────────────────────
    path('api/v1/agent/', include([
        path('auth/', include('apps.accounts.urls_agent')),
        path('properties/', include('apps.properties.urls_agent')),
        path('bookings/', include('apps.bookings.urls_agent')),
        path('offers/', include('apps.offers.urls_agent')),
        path('notifications/', include('apps.notifications.urls_role')),
        path('boards/', include('apps.qr_boards.urls')),
    ])),

    # ── Admin Scope ──────────────────────────────────────────────────
    path('api/v1/admin/', include('apps.admin_panel.urls')),

    # ── Neutral / Public Endpoints ──────────────────────────────────
    path('api/v1/qr/', include('apps.qr_boards.redirect_urls')),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
