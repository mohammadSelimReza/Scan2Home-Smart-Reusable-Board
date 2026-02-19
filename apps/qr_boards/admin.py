from django.contrib import admin
from .models import QRBoard, BoardAssignment


@admin.register(QRBoard)
class QRBoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'agent', 'scan_count', 'created_at')
    search_fields = ('agent__email', 'agent__full_name')


@admin.register(BoardAssignment)
class BoardAssignmentAdmin(admin.ModelAdmin):
    list_display = ('board', 'property', 'is_active', 'assigned_at')
    list_filter = ('is_active',)
