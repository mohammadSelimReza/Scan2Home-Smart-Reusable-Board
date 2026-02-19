from django.urls import path, include

# ── User (Buyer) Scope ──────────────────────────────────────────
user_patterns = [
    path('auth/', include([
        path('', include('apps.accounts.urls_user')), # To be created
    ])),
    path('properties/', include('apps.properties.urls_user')), # To be created
    path('bookings/', include('apps.bookings.urls_user')),    # To be created
    path('offers/', include('apps.offers.urls_user')),        # To be created
    path('notifications/', include('apps.notifications.urls_user')), # To be created
    path('chat/', include('apps.chat.urls')),
    path('qr/', include('apps.qr_boards.redirect_urls')),
]

# ── Agent (Seller) Scope ─────────────────────────────────────────
agent_patterns = [
    path('auth/', include([
        path('', include('apps.accounts.urls_agent')), # To be created
    ])),
    path('properties/', include('apps.properties.urls_agent')), # To be created
    path('boards/', include('apps.qr_boards.urls')),
    path('offers/', include('apps.offers.urls_agent')),         # To be created
    path('bookings/', include('apps.bookings.urls_agent')),    # To be created
    path('notifications/', include('apps.notifications.urls_agent')), # To be created
]

# ── Admin Scope ──────────────────────────────────────────────────
admin_patterns = [
    path('', include('apps.admin_panel.urls')),
]
