import time
import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('request')


class UpdateLastActiveMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            User.objects.filter(pk=request.user.pk).update(last_active=timezone.now())
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """Logs every request with: timestamp | method | path | user | status | duration."""

    def process_request(self, request):
        request._req_start = time.time()

    def process_response(self, request, response):
        duration_ms = 0
        if hasattr(request, '_req_start'):
            duration_ms = int((time.time() - request._req_start) * 1000)

        user = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.email or str(request.user)

        logger.info(
            '%s | %s %s | %s | %s | %dms',
            timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            request.method,
            request.get_full_path(),
            user,
            response.status_code,
            duration_ms,
        )
        return response
