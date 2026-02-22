from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse

from .models import Offer, CounterOffer
from .serializers import OfferSerializer, CounterOfferSerializer, CounterOfferCreateSerializer
from apps.accounts.permissions import IsAgent
from apps.notifications.services import NotificationService
from apps.common.doc_examples import OFFER_CREATE_REQUEST, COUNTER_OFFER_REQUEST


class SubmitOfferView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=OfferSerializer,
        responses=OfferSerializer,
        examples=[OFFER_CREATE_REQUEST],
        tags=['Offers']
    )
    def post(self, request):
        serializer = OfferSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        # Notify agent
        NotificationService.create(
            user=offer.property.agent,
            title='New Offer Received!',
            body=f'{offer.buyer_name} made an offer of ${offer.offer_amount} on "{offer.property.title}".',
            notification_type='offer',
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AgentOfferListView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(
        tags=['Offers'],
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status (pending, accepted, rejected)'),
        ],
        responses=OfferSerializer(many=True)
    )
    def get(self, request):
        qs = Offer.objects.filter(
            property__agent=request.user
        ).select_related('property').prefetch_related('counter_offers')

        status_filter = request.query_params.get('status')
        if status_filter and status_filter != 'all':
            qs = qs.filter(status=status_filter)

        serializer = OfferSerializer(qs, many=True, context={'request': request})
        return Response({'count': qs.count(), 'results': serializer.data})


class AgentOfferActionView(APIView):
    permission_classes = [IsAgent]

    def get_offer(self, request, offer_id):
        return get_object_or_404(Offer, id=offer_id, property__agent=request.user)

    @extend_schema(
        tags=['Offers'],
        request=None,
        responses=OpenApiResponse(description="Action performed")
    )
    def post(self, request, offer_id, action):
        offer = self.get_offer(request, offer_id)
        if action == 'accept':
            offer.status = 'accepted'
            offer.save()
            return Response({'message': 'Offer accepted.'})
        elif action == 'reject':
            offer.status = 'rejected'
            offer.save()
            return Response({'message': 'Offer rejected.'})
        elif action == 'lead':
            offer.is_lead = True
            offer.save()
            return Response({'message': 'Added to leads.'})
        return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)


class CounterOfferView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(
        request=CounterOfferCreateSerializer,
        responses=CounterOfferSerializer,
        examples=[COUNTER_OFFER_REQUEST],
        tags=['Offers']
    )
    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, id=offer_id, property__agent=request.user)
        serializer = CounterOfferCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        counter = CounterOffer.objects.create(offer=offer, by_agent=True, **serializer.validated_data)
        return Response(CounterOfferSerializer(counter).data, status=status.HTTP_201_CREATED)


class OfferHistoryView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(responses=OfferSerializer, tags=['Offers'])
    def get(self, request, offer_id):
        offer = get_object_or_404(Offer, id=offer_id, property__agent=request.user)
        return Response(OfferSerializer(offer, context={'request': request}).data)
