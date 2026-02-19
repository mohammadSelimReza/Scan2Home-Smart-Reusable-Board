from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes

from .models import Property, PropertyImage, PropertyVideo, PropertyFavourite, SupportMessage
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer,
    PropertyCreateUpdateSerializer, PropertyImageUploadSerializer,
    FavouriteSerializer, PropertyVideoUploadSerializer, SupportMessageSerializer
)
from apps.accounts.permissions import IsAgent


class PropertyListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Properties'],
        parameters=[
            OpenApiParameter('type', OpenApiTypes.STR, description='Filter by property type (apartment, villa, etc)'),
            OpenApiParameter('price_min', OpenApiTypes.DECIMAL, description='Minimum price'),
            OpenApiParameter('price_max', OpenApiTypes.DECIMAL, description='Maximum price'),
            OpenApiParameter('beds', OpenApiTypes.STR, description='Number of beds (e.g. 1, 2, 5+)'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by title, address, postcode'),
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
        ptype = request.query_params.get('type')
        if ptype:
            qs = qs.filter(property_type=ptype)

        price_min = request.query_params.get('price_min')
        if price_min:
            qs = qs.filter(price__gte=price_min)

        price_max = request.query_params.get('price_max')
        if price_max:
            qs = qs.filter(price__lte=price_max)

        beds = request.query_params.get('beds')
        if beds and beds != 'any':
            if beds == '5+':
                qs = qs.filter(beds__gte=5)
            else:
                qs = qs.filter(beds=beds)

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(address__icontains=search) |
                Q(postcode__icontains=search)
            )

        # Amenities
        amenities = {
            'pool': 'has_pool', 'pet_friendly': 'is_pet_friendly',
            'garden': 'has_garden', 'parking': 'parking_slots__gt',
        }
        for param, field in amenities.items():
            if request.query_params.get(param) == 'true':
                if 'gt' in field:
                    qs = qs.filter(**{field: 0})
                else:
                    qs = qs.filter(**{field: True})

        serializer = PropertyListSerializer(qs, many=True, context={'request': request})
        return Response({'count': qs.count(), 'results': serializer.data})


class PropertyCreateView(APIView):
    permission_classes = [IsAgent]

    @extend_schema(request=PropertyCreateUpdateSerializer, responses=PropertyDetailSerializer, tags=['Properties'])
    def post(self, request):
        serializer = PropertyCreateUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        property_ = serializer.save()
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
