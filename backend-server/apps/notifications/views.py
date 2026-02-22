from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Notification, UserNotificationSettings
from .serializers import NotificationSerializer, NotificationSettingsSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=NotificationSerializer(many=True), tags=['Notifications'])
    def get(self, request):
        notifs = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifs, many=True)
        return Response(serializer.data)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=OpenApiResponse(description="Marked as read"), tags=['Notifications'])
    def post(self, request, pk):
        Notification.objects.filter(user=request.user, pk=pk).update(is_read=True)
        return Response({'message': 'Marked as read.'})


class NotificationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=NotificationSettingsSerializer, tags=['Notifications'])
    def get(self, request):
        settings_obj, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
        return Response(NotificationSettingsSerializer(settings_obj).data)

    @extend_schema(request=NotificationSettingsSerializer, responses=NotificationSettingsSerializer, tags=['Notifications'])
    def patch(self, request):
        settings_obj, _ = UserNotificationSettings.objects.get_or_create(user=request.user)
        serializer = NotificationSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
