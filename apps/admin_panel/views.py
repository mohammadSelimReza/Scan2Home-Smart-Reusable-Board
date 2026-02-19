from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.accounts.permissions import IsAdminUser
from apps.properties.models import Property, SupportMessage, StaticPage, PropertyType2
from apps.accounts.models import AgentProfile

from .serializers import (
    AdminDashboardSerializer, AdminActionResponseSerializer,
    PropertyTypeSerializer, AdminSupportMessageSerializer, SupportReplySerializer
)

User = get_user_model()


# ── Dashboard ─────────────────────────────────────────────────

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(responses=AdminDashboardSerializer, tags=['Admin'])
    def get(self, request):
        return Response({
            'total_users': User.objects.filter(role='buyer').count(),
            'total_agents': User.objects.filter(role='agent').count(),
            'total_agents_verified': AgentProfile.objects.filter(is_verified=True).count(),
            'total_agents_pending': AgentProfile.objects.filter(is_verified=False).count(),
            'total_properties': Property.objects.count(),
            'total_properties_approved': Property.objects.filter(is_approved=True).count(),
            'total_properties_pending': Property.objects.filter(is_approved=False).count(),
            'property_by_type': dict(
                Property.objects.values_list('property_type').annotate(c=Count('id')).values_list('property_type', 'c')
            ),
        })


# ── Property Management ───────────────────────────────────────

class AdminPropertyListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Admin'])
    def get(self, request):
        qs = Property.objects.select_related('agent').prefetch_related('images')
        status_filter = request.query_params.get('status')
        type_filter = request.query_params.get('type')
        search = request.query_params.get('search')
        if status_filter and status_filter != 'all':
            is_approved = status_filter == 'approved'
            qs = qs.filter(is_approved=is_approved)
        if type_filter:
            qs = qs.filter(property_type=type_filter)
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(address__icontains=search))

        from apps.properties.serializers import PropertyListSerializer
        serializer = PropertyListSerializer(qs, many=True, context={'request': request})
        return Response({'count': qs.count(), 'results': serializer.data})


class AdminPropertyActionView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=None, responses=AdminActionResponseSerializer, tags=['Admin'])
    def post(self, request, pk, action):
        prop = get_object_or_404(Property, pk=pk)
        if action == 'approve':
            prop.is_approved = True
            prop.save()
            return Response({'message': 'Property approved.'})
        elif action == 'reject':
            prop.is_approved = False
            prop.save()
            return Response({'message': 'Property rejected.'})
        return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)


# ── User Management ───────────────────────────────────────────

class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Admin'])
    def get(self, request):
        from apps.accounts.serializers import UserProfileSerializer
        qs = User.objects.filter(role='buyer').order_by('-member_since')
        serializer = UserProfileSerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Admin'])
    def get(self, request, pk):
        from apps.accounts.serializers import UserProfileSerializer
        user = get_object_or_404(User, pk=pk)
        return Response(UserProfileSerializer(user).data)

    @extend_schema(request=None, responses=AdminActionResponseSerializer, tags=['Admin'])
    def post(self, request, pk):
        """Ban / Unban user"""
        user = get_object_or_404(User, pk=pk)
        user.is_banned = not user.is_banned
        user.save()
        action = 'banned' if user.is_banned else 'unbanned'
        return Response({'message': f'User {action}.'})


# ── Agent Management ──────────────────────────────────────────

class AdminAgentListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Admin'])
    def get(self, request):
        from apps.accounts.serializers import UserProfileSerializer
        qs = User.objects.filter(role='agent').select_related('agent_profile').order_by('-member_since')
        serializer = UserProfileSerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})


class AdminAgentVerifyView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=None, responses=AdminActionResponseSerializer, tags=['Admin'])
    def post(self, request, pk):
        agent_profile = get_object_or_404(AgentProfile, user__pk=pk)
        agent_profile.is_verified = not agent_profile.is_verified
        agent_profile.save()
        state = 'verified' if agent_profile.is_verified else 'unverified'
        return Response({'message': f'Agent {state}.'})


class AdminAgentBanView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=None, responses=AdminActionResponseSerializer, tags=['Admin'])
    def post(self, request, pk):
        agent = get_object_or_404(User, pk=pk, role='agent')
        agent.is_banned = not agent.is_banned
        agent.save()
        action = 'banned' if agent.is_banned else 'unbanned'
        return Response({'message': f'Agent {action}.'})


# ── Settings ──────────────────────────────────────────────────

class StaticPageView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Admin Settings'])
    def get(self, request, page_type):
        page, _ = StaticPage.objects.get_or_create(page_type=page_type, defaults={'content': ''})
        return Response({'page_type': page.page_type, 'content': page.content})

    @extend_schema(tags=['Admin Settings'])
    def put(self, request, page_type):
        page, _ = StaticPage.objects.get_or_create(page_type=page_type, defaults={'content': ''})
        page.content = request.data.get('content', '')
        page.save()
        return Response({'page_type': page.page_type, 'content': page.content})


class PublicStaticPageView(APIView):
    """Public endpoint for buyers to read T&C / Privacy"""
    permission_classes = []
    authentication_classes = []

    @extend_schema(tags=['Public'])
    def get(self, request, page_type):
        page = get_object_or_404(StaticPage, page_type=page_type)
        return Response({'page_type': page.page_type, 'content': page.content})


class PropertyTypeConfigView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(responses=PropertyTypeSerializer(many=True), tags=['Admin Settings'])
    def get(self, request):
        types = PropertyType2.objects.all()
        return Response([{'name': t.name, 'slug': t.slug} for t in types])

    @extend_schema(request=PropertyTypeSerializer, responses=PropertyTypeSerializer, tags=['Admin Settings'])
    def post(self, request):
        from django.utils.text import slugify
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error': 'name required.'}, status=status.HTTP_400_BAD_REQUEST)
        obj, _ = PropertyType2.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
        return Response({'name': obj.name, 'slug': obj.slug}, status=status.HTTP_201_CREATED)

    @extend_schema(request=PropertyTypeSerializer, responses=OpenApiResponse(description="Deleted"), tags=['Admin Settings'])
    def delete(self, request):
        slug = request.data.get('slug')
        PropertyType2.objects.filter(slug=slug).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupportMessageListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(responses=AdminSupportMessageSerializer(many=True), tags=['Admin Settings'])
    def get(self, request):
        msgs = SupportMessage.objects.select_related('user').order_by('-created_at')
        return Response(AdminSupportMessageSerializer(msgs, many=True).data)


class SupportMessageReplyView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=SupportReplySerializer, responses=AdminActionResponseSerializer, tags=['Admin Settings'])
    def post(self, request, pk):
        from django.utils import timezone
        msg = get_object_or_404(SupportMessage, pk=pk)
        msg.reply = request.data.get('reply', '')
        msg.is_replied = True
        msg.replied_at = timezone.now()
        msg.save()
        return Response({'message': 'Reply sent.'})
