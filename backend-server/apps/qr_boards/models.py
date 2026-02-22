import uuid
import os
import qrcode
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files import File


class QRBoard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='qr_boards', limit_choices_to={'role': 'agent'}
    )
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    scan_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qr_boards'
        ordering = ['-created_at']

    def __str__(self):
        return f'QRBoard {self.id} (Agent: {self.agent.full_name})'

    def generate_qr_code(self):
        """Generate QR code image pointing to the QR redirect endpoint."""
        qr_url = f"{settings.FRONTEND_URL}/scan/{self.id}/"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'qr_{self.id}.png'
        self.qr_code_image.save(filename, File(buffer), save=True)

    @property
    def active_property(self):
        assignment = self.assignments.filter(is_active=True).select_related('property').first()
        return assignment.property if assignment else None


class BoardAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(QRBoard, on_delete=models.CASCADE, related_name='assignments')
    property = models.ForeignKey(
        'properties.Property', on_delete=models.CASCADE, related_name='board_assignments'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'board_assignments'
        ordering = ['-assigned_at']

    def __str__(self):
        return f'Board {self.board_id} → Property {self.property_id} (active={self.is_active})'
