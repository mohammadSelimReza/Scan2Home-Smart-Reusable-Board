from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timesince import timesince
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes

from .models import (
    Property, PropertyImage, PropertyVideo, PropertyFavourite, 
    SupportMessage, PropertyType, PropertyType2
)
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer,
    PropertyCreateUpdateSerializer, PropertyImageUploadSerializer,
    FavouriteSerializer, PropertyVideoUploadSerializer, SupportMessageSerializer
)
from apps.accounts.permissions import IsAgent
from apps.common.doc_examples import PROPERTY_CREATE_REQUEST, PROPERTY_RESPONSE
from apps.notifications.services import NotificationService


class PropertyListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Properties'],
        parameters=[
            OpenApiParameter('property_type', OpenApiTypes.STR, description='Filter by property type (e.g. houses, apartment). Default is all'),
            OpenApiParameter('type', OpenApiTypes.STR, description='Filter by property type (apartment, villa, etc)'),
            OpenApiParameter('price_min', OpenApiTypes.DECIMAL, description='Minimum price (legacy)'),
            OpenApiParameter('min_price', OpenApiTypes.DECIMAL, description='Minimum price (default 0)'),
            OpenApiParameter('price_max', OpenApiTypes.DECIMAL, description='Maximum price (legacy)'),
            OpenApiParameter('max_price', OpenApiTypes.DECIMAL, description='Maximum price'),
            OpenApiParameter('beds', OpenApiTypes.STR, description='Number of beds (e.g. 1, 2, 5+)'),
            OpenApiParameter('text_search', OpenApiTypes.STR, description='Search by text (title, address, postcode)'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by title, address, postcode'),
            OpenApiParameter('amenities', OpenApiTypes.STR, description='Filter by amenities (comma-separated, e.g. "parking,pool")'),
            OpenApiParameter('pool', OpenApiTypes.BOOL, description='Has pool'),
            OpenApiParameter('pet_friendly', OpenApiTypes.BOOL, description='Is pet friendly'),
            OpenApiParameter('garden', OpenApiTypes.BOOL, description='Has garden'),
            OpenApiParameter('parking', OpenApiTypes.BOOL, description='Has parking'),
        ],
        responses=PropertyListSerializer(many=True)
    )
    def get(self, request):
        qs = Property.objects.filter(is_approved=True).select_related('agent__agent_profile').prefetch_related('images')

        # Filters
        property_type_param = request.query_params.get('property_type', 'all')
        if property_type_param and property_type_param.lower() != 'all':
            qs = qs.filter(property_type=property_type_param)
        else:
            # Fallback to older 'type' parameter
            ptype = request.query_params.get('type')
            if ptype:
                qs = qs.filter(property_type=ptype)

        price_min = request.query_params.get('price_min')
        min_price = request.query_params.get('min_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        elif price_min:
            qs = qs.filter(price__gte=price_min)
        else:
            # By default min_price should be 0
            qs = qs.filter(price__gte=0)

        price_max = request.query_params.get('price_max')
        max_price = request.query_params.get('max_price')
        
        if max_price:
            qs = qs.filter(price__lte=max_price)
        elif price_max:
            qs = qs.filter(price__lte=price_max)

        beds = request.query_params.get('beds')
        if beds and beds != 'any':
            if beds == '5+':
                qs = qs.filter(beds__gte=5)
            else:
                qs = qs.filter(beds=beds)

        text_search_param = request.query_params.get('text_search', '').strip(' "')
        if text_search_param:
            qs = qs.filter(
                Q(title__icontains=text_search_param) |
                Q(address__icontains=text_search_param) |
                Q(postcode__icontains=text_search_param)
            )
        else:
            search = request.query_params.get('search')
            if search:
                qs = qs.filter(
                    Q(title__icontains=search) |
                    Q(address__icontains=search) |
                    Q(postcode__icontains=search)
                )

        # Amenities
        amenities_param = request.query_params.get('amenities', '')
        if amenities_param:
            amenity_list = [a.strip().lower() for a in amenities_param.split(',')]
            for amenity in amenity_list:
                if amenity == 'pool':
                    qs = qs.filter(has_pool=True)
                elif amenity in ['pet', 'pet_friendly', 'pets']:
                    qs = qs.filter(is_pet_friendly=True)
                elif amenity == 'garden':
                    qs = qs.filter(has_garden=True)
                elif amenity == 'parking':
                    qs = qs.filter(parking_slots__gt=0)
                elif amenity == 'garage':
                    qs = qs.filter(has_garage=True)
                elif amenity == 'gym':
                    qs = qs.filter(has_gym=True)
                elif amenity == 'smart_home':
                    qs = qs.filter(is_smart_home=True)
                elif amenity == 'fireplace':
                    qs = qs.filter(has_fireplace=True)
                    
        legacy_amenities = {
            'pool': 'has_pool', 'pet_friendly': 'is_pet_friendly',
            'garden': 'has_garden', 'parking': 'parking_slots__gt',
        }
        for param, field in legacy_amenities.items():
            if request.query_params.get(param) == 'true':
                if 'gt' in field:
                    qs = qs.filter(**{field: 0})
                else:
                    qs = qs.filter(**{field: True})

        serializer = PropertyListSerializer(qs, many=True, context={'request': request})
        return Response({'count': qs.count(), 'results': serializer.data})


class PropertyCreateView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(
        request=PropertyCreateUpdateSerializer,
        responses=PropertyDetailSerializer,
        examples=[PROPERTY_CREATE_REQUEST, PROPERTY_RESPONSE],
        tags=['Properties']
    )
    def post(self, request):
        serializer = PropertyCreateUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        property_ = serializer.save()

        # Track property creation
        NotificationService.create(
            user=request.user,
            title=property_.title,
            body=f'You listed a new property: "{property_.title}".',
            notification_type='property',
        )

        return Response(PropertyDetailSerializer(property_, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)


class PropertyDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(
            Property.objects.select_related('agent__agent_profile').prefetch_related('images', 'video'),
            pk=pk
        )

    @extend_schema(responses=PropertyDetailSerializer, tags=['Properties'])
    def get(self, request, pk):
        prop = self.get_object(pk)
        # Increment views
        Property.objects.filter(pk=pk).update(views_count=prop.views_count + 1)

        # Track property visit (notify the agent)
        if request.user.is_authenticated and request.user != prop.agent:
            NotificationService.create(
                user=prop.agent,
                title=prop.title,
                body=f'Your property "{prop.title}" was visited by a user.',
                notification_type='property',
            )

        serializer = PropertyDetailSerializer(prop, context={'request': request})
        return Response(serializer.data)

    @extend_schema(request=PropertyCreateUpdateSerializer, responses=PropertyDetailSerializer, tags=['Properties'])
    def patch(self, request, pk):
        prop = self.get_object(pk)
        if prop.agent != request.user:
            return Response({'error': 'Not your property.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PropertyCreateUpdateSerializer(prop, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Track property update
        NotificationService.create(
            user=request.user,
            title=prop.title,
            body=f'You updated property: "{prop.title}".',
            notification_type='property',
        )

        return Response(PropertyDetailSerializer(prop, context={'request': request}).data)

    @extend_schema(responses=OpenApiResponse(description="Property deleted"), tags=['Properties'])
    def delete(self, request, pk):
        prop = self.get_object(pk)
        if prop.agent != request.user:
            return Response({'error': 'Not your property.'}, status=status.HTTP_403_FORBIDDEN)
        prop.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyImageUploadView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(request=PropertyImageUploadSerializer, responses=PropertyImageUploadSerializer, tags=['Properties'])
    def post(self, request, pk):
        prop = get_object_or_404(Property, pk=pk, agent=request.user)
        serializer = PropertyImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save(property=prop)
        return Response(PropertyImageUploadSerializer(image).data, status=status.HTTP_201_CREATED)


class PropertyVideoUploadView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(request=PropertyVideoUploadSerializer, responses=OpenApiResponse(description="Video uploaded"), tags=['Properties'])
    def post(self, request, pk):
        prop = get_object_or_404(Property, pk=pk, agent=request.user)
        video_file = request.FILES.get('video_file')
        if not video_file:
            return Response({'error': 'video_file is required.'}, status=status.HTTP_400_BAD_REQUEST)
        PropertyVideo.objects.filter(property=prop).delete()
        PropertyVideo.objects.create(property=prop, video_file=video_file)
        return Response({'message': 'Video uploaded.'}, status=status.HTTP_201_CREATED)


class FavouriteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=OpenApiResponse(description="Favourited status toggled"), tags=['Favourites'])
    def post(self, request, pk):
        prop = get_object_or_404(Property, pk=pk)
        fav, created = PropertyFavourite.objects.get_or_create(user=request.user, property=prop)
        if not created:
            fav.delete()
            return Response({'favourited': False})
        return Response({'favourited': True}, status=status.HTTP_201_CREATED)


class FavouriteListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=FavouriteSerializer(many=True), tags=['Favourites'])
    def get(self, request):
        qs = PropertyFavourite.objects.filter(user=request.user).select_related(
            'property__agent__agent_profile'
        ).prefetch_related('property__images')
        ptype = request.query_params.get('type')
        if ptype:
            qs = qs.filter(property__property_type=ptype)
        serializer = FavouriteSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class AgentPropertyListView(APIView):
    """Agent's own property list"""
    permission_classes = [IsAgent]

    @extend_schema(responses=PropertyListSerializer(many=True), tags=['Properties'])
    def get(self, request):
        qs = Property.objects.filter(agent=request.user).prefetch_related('images')
        serializer = PropertyListSerializer(qs, many=True, context={'request': request})
        return Response({'count': qs.count(), 'results': serializer.data})


class SimilarPropertyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=PropertyListSerializer(many=True), tags=['Properties'])
    def get(self, request, pk):
        prop = get_object_or_404(Property, pk=pk)
        similar = Property.objects.filter(
            property_type=prop.property_type, is_approved=True
        ).exclude(pk=pk).prefetch_related('images')[:6]
        serializer = PropertyListSerializer(similar, many=True, context={'request': request})
        return Response(serializer.data)


class UserSupportMessageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=SupportMessageSerializer, responses=OpenApiResponse(description="Support request sent"), tags=['Support'])
    def post(self, request):
        serializer = SupportMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        SupportMessage.objects.create(user=request.user, message=serializer.validated_data['message'])
        return Response({'message': 'Support request sent.'}, status=status.HTTP_201_CREATED)


class AgentDashboardView(APIView):
    """Agent dashboard overview with key stats and recent activity."""
    permission_classes = [IsAgent]

    @extend_schema(
        responses=OpenApiResponse(description="Agent dashboard overview"),
        tags=['Properties']
    )
    def get(self, request):
        agent = request.user
        agent_properties = Property.objects.filter(agent=agent)

        # Aggregate stats
        aggregates = agent_properties.aggregate(
            total_views=Sum('views_count'),
            total_qr_scanned=Sum('qr_scanned_count'),
        )

        from apps.offers.models import Offer
        from apps.notifications.models import Notification

        total_offers = Offer.objects.filter(property__agent=agent).count()

        # Recent activity from notifications (covers all: property, offer, booking, qr_scan)
        notifications = Notification.objects.filter(
            user=agent
        ).order_by('-created_at')[:10]

        recent_activity = [
            {
                'property_name': notif.title,
                'activity': notif.body,
                'type': notif.notification_type,
                'time': timesince(notif.created_at, timezone.now()) + ' ago',
            }
            for notif in notifications
        ]

        return Response({
            'total_property_listing': agent_properties.count(),
            'total_property_views': aggregates['total_views'] or 0,
            'total_offers_received': total_offers,
            'total_qr_scanned': aggregates['total_qr_scanned'] or 0,
            'recent_activity': recent_activity,
        })


class PropertyTypeListView(APIView):
    """List of available property types for filtering."""
    permission_classes = [AllowAny]

    @extend_schema(
        responses=OpenApiResponse(description="List of property type strings"),
        tags=['Properties']
    )
    def get(self, request):
        # 1. Start with hardcoded choices from PropertyType enum
        types = set(choice.value for choice in PropertyType)

        # 2. Add any types from PropertyType2 (admin-configurable)
        custom_types = PropertyType2.objects.values_list('slug', flat=True)
        types.update(custom_types)

        # 3. Add any existing types from Property model just in case some exist that aren't in the above
        existing_types = Property.objects.values_list('property_type', flat=True).distinct()
        types.update(existing_types)

        return Response(sorted(list(types)))
