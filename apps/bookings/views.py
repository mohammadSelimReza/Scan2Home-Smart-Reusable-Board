from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Booking
from .serializers import BookingSerializer
from apps.accounts.permissions import IsAgent
from apps.notifications.services import NotificationService


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=BookingSerializer, responses=BookingSerializer, tags=['Bookings'])
    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Notify agent
        NotificationService.create(
            user=booking.property.agent,
            title='New Viewing Booked!',
            body=f'{booking.buyer.full_name} booked a viewing for "{booking.property.title}" on {booking.date}.',
            notification_type='booking',
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=BookingSerializer(many=True), tags=['Bookings'])
    def get(self, request):
        qs = Booking.objects.filter(buyer=request.user).select_related('property')
        serializer = BookingSerializer(qs, many=True)
        return Response(serializer.data)


class AgentBookingsView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(responses=BookingSerializer(many=True), tags=['Bookings'])
    def get(self, request):
        qs = Booking.objects.filter(
            property__agent=request.user
        ).select_related('property', 'buyer')
        serializer = BookingSerializer(qs, many=True)
        return Response(serializer.data)


class BookingActionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Bookings'],
        request=None,
        responses=BookingSerializer
    )
    def post(self, request, pk, action):
        booking = get_object_or_404(Booking, pk=pk)

        # agent can confirm/cancel; buyer can cancel own booking
        if action == 'confirm':
            if not request.user.role == 'agent' or booking.property.agent != request.user:
                return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
            booking.status = 'confirmed'
        elif action == 'cancel':
            if booking.buyer != request.user and booking.property.agent != request.user:
                return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
            booking.status = 'cancelled'
        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

        booking.save()
        return Response(BookingSerializer(booking).data)
