import asyncio
import threading
from channels.layers import get_channel_layer
from .models import Notification


class NotificationService:
    @staticmethod
    def create(user, title: str, body: str, notification_type: str = 'system') -> Notification:
        """Create a DB notification and push it over WebSocket (non-blocking)."""
        notif = Notification.objects.create(
            user=user,
            title=title,
            body=body,
            notification_type=notification_type,
        )

        # Push WS in a daemon thread using its own asyncio event loop
        # This is safe for Gunicorn sync workers
        payload = {
            'id': str(notif.id),
            'title': notif.title,
            'body': notif.body,
            'notification_type': notif.notification_type,
            'created_at': notif.created_at.isoformat(),
        }
        group_name = f'notifications_{user.id}'

        def push():
            async def _send():
                try:
                    layer = get_channel_layer()
                    await layer.group_send(
                        group_name,
                        {'type': 'notification_message', 'data': payload}
                    )
                except Exception:
                    pass

            try:
                asyncio.run(_send())
            except Exception:
                pass

        threading.Thread(target=push, daemon=True).start()

        return notif
