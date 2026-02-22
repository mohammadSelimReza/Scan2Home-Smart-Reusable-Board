import uuid
from django.db import models
from django.conf import settings


class NotificationType(models.TextChoices):
    QR_SCAN = 'qr_scan', 'QR Scan'
    OFFER = 'offer', 'Offer'
    BOOKING = 'booking', 'Booking'
    SYSTEM = 'system', 'System'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications_list'
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notif for {self.user.email}: {self.title}'


class UserNotificationSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_settings'
    )
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_notification_settings'

    def __str__(self):
        return f'NotifSettings for {self.user.email}'
