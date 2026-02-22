from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiTypes

from .models import QRBoard, BoardAssignment
from .serializers import QRBoardSerializer, ReassignBoardSerializer
from apps.accounts.permissions import IsAgent
from apps.properties.models import Property
from apps.notifications.services import NotificationService
from apps.common.doc_examples import REASSIGN_BOARD_REQUEST


class QRBoardListCreateView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(responses=QRBoardSerializer(many=True), tags=['QR Boards'])
    def get(self, request):
        boards = QRBoard.objects.filter(agent=request.user).prefetch_related('assignments__property')
        serializer = QRBoardSerializer(boards, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(request=None, responses=QRBoardSerializer, tags=['QR Boards'])
    def post(self, request):
        board = QRBoard.objects.create(agent=request.user)
        board.generate_qr_code()  # generates and saves QR image
        serializer = QRBoardSerializer(board, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QRBoardDetailView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(responses=QRBoardSerializer, tags=['QR Boards'])
    def get(self, request, qr_id):
        board = get_object_or_404(QRBoard, id=qr_id, agent=request.user)
        return Response(QRBoardSerializer(board, context={'request': request}).data)


class QRBoardReassignView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(
        request=ReassignBoardSerializer,
        responses=QRBoardSerializer,
        examples=[REASSIGN_BOARD_REQUEST],
        tags=['QR Boards']
    )
    def patch(self, request, qr_id):
        board = get_object_or_404(QRBoard, id=qr_id, agent=request.user)
        serializer = ReassignBoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        property_id = serializer.validated_data['property_id']
        try:
            prop = Property.objects.get(id=property_id, agent=request.user)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)

        # Deactivate previous assignment
        BoardAssignment.objects.filter(board=board, is_active=True).update(is_active=False)

        # Create new active assignment
        BoardAssignment.objects.create(board=board, property=prop, is_active=True)

        return Response(QRBoardSerializer(board, context={'request': request}).data)


class QRBoardDownloadView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(responses=OpenApiResponse(description="QR Code URL", response={'type': 'object', 'properties': {'qr_code_url': {'type': 'string'}}}), tags=['QR Boards'])
    def get(self, request, qr_id):
        board = get_object_or_404(QRBoard, id=qr_id, agent=request.user)
        if not board.qr_code_image:
            return Response({'error': 'No QR code generated yet.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'qr_code_url': request.build_absolute_uri(board.qr_code_image.url)})


class QRScanRedirectView(APIView):
    """Public endpoint: scanned by buyer → redirect to property page + log scan"""
    permission_classes = []
    authentication_classes = []

    @extend_schema(responses=OpenApiResponse(description="Redirect URL", response={'type': 'object', 'properties': {'redirect_url': {'type': 'string'}, 'property_id': {'type': 'string'}}}), tags=['QR Boards'])
    def get(self, request, qr_id):
        board = get_object_or_404(QRBoard, id=qr_id)
        assignment = board.assignments.filter(is_active=True).select_related('property', 'property__agent').first()

        if not assignment:
            return Response({'error': 'This board has no active property.'}, status=status.HTTP_404_NOT_FOUND)

        # Increment scan counts
        QRBoard.objects.filter(id=qr_id).update(scan_count=board.scan_count + 1)
        Property.objects.filter(id=assignment.property.id).update(
            qr_scanned_count=assignment.property.qr_scanned_count + 1
        )

        # Notify agent
        NotificationService.create(
            user=assignment.property.agent,
            title='QR Code Scanned!',
            body=f'Someone scanned the QR code for "{assignment.property.title}".',
            notification_type='qr_scan',
        )

        # Return redirect URL
        from django.conf import settings
        redirect_url = f"{settings.FRONTEND_URL}/properties/{assignment.property.id}/"
        return Response({'redirect_url': redirect_url, 'property_id': str(assignment.property.id)})
