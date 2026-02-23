from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiTypes

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
        from apps.properties.serializers import PropertyListSerializer
        from apps.accounts.serializers import UserProfileSerializer
        
        activities = []
        # Add new users
        for u in User.objects.all().order_by('-member_since')[:5]:
            activities.append({
                'id': str(u.id),
                'user': UserProfileSerializer(u).data,
                'action': 'registered',
                'timestamp': u.member_since,
                'details': f"New {u.role} registered."
            })
            
        # Add property creations
        for p in Property.objects.all().order_by('-created_at')[:5]:
            activities.append({
                'id': str(p.id),
                'user': UserProfileSerializer(p.agent).data,
                'action': 'created_property',
                'timestamp': p.created_at,
                'details': f"Added property: {p.title}"
            })

        # Add support messages
        for msg in SupportMessage.objects.all().order_by('-created_at')[:5]:
            activities.append({
                'id': str(msg.id),
                'user': UserProfileSerializer(msg.user).data,
                'action': 'sent_support_message',
                'timestamp': msg.created_at,
                'details': f"Sent message: {msg.message[:30]}..."
            })
            
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activities = activities[:5]

        return Response({
            'total_users': User.objects.filter(role='buyer').count(),
            'total_agents': User.objects.filter(role='agent').count(),
            'total_agents_verified': AgentProfile.objects.filter(is_verified=True).count(),
            'total_agents_pending': AgentProfile.objects.filter(is_verified=False).count(),
            'total_properties': Property.objects.count(),
            'total_properties_approved': Property.objects.filter(is_approved=True).count(),
            'total_properties_pending': Property.objects.filter(is_approved=False).count(),
            'total_views_counts': Property.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0,
            'property_by_type': dict(
                Property.objects.values_list('property_type').annotate(c=Count('id')).values_list('property_type', 'c')
            ),
            'latest_requested_properties': PropertyListSerializer(
                Property.objects.filter(is_approved=False).order_by('-created_at')[:5], 
                many=True, 
                context={'request': request}
            ).data,
            'recent_user_activities': recent_activities,
        })


# ── Property Management ───────────────────────────────────────

class AdminPropertyListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin'], 
        operation_id='v1_admin_property_list_retrieve',
        parameters=[
            OpenApiParameter('approval_status', OpenApiTypes.STR, description='Filter by approval status (all, approved, pending)'),
            OpenApiParameter('property_types', OpenApiTypes.STR, description='Filter by property types (comma separated string "house,apartment")'),
            OpenApiParameter('status', OpenApiTypes.STR, description='(Legacy) Filter by approval status (all, approved, pending)'),
            OpenApiParameter('type', OpenApiTypes.STR, description='(Legacy) Filter by property type'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search text'),
        ],
        responses={'200': {'type': 'object', 'properties': {'count': {'type': 'integer'}, 'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/AdminProperty'}}}}})
    def get(self, request):
        qs = Property.objects.select_related('agent').prefetch_related('images')
        
        # Approval status (all / approved / pending)
        status_filter = request.query_params.get('status')
        approval_status = request.query_params.get('approval_status')
        
        active_status = approval_status or status_filter
        
        if active_status and active_status != 'all':
            if active_status == 'approved':
                qs = qs.filter(is_approved=True)
            elif active_status == 'pending':
                qs = qs.filter(is_approved=False)
                
        # Property types (comma separated string "house,apartment")
        type_filter = request.query_params.get('type')
        property_types = request.query_params.get('property_types')
        
        if property_types:
            types_list = [t.strip().lower() for t in property_types.split(',') if t.strip()]
            if types_list:
                qs = qs.filter(property_type__in=types_list)
        elif type_filter:
            qs = qs.filter(property_type=type_filter)
            
        search = request.query_params.get('search')
        
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(address__icontains=search))

        from apps.properties.serializers import AdminPropertySerializer
        serializer = AdminPropertySerializer(qs, many=True, context={'request': request})
        return Response({'count': qs.count(), 'results': serializer.data})


class AdminPropertyDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin'], 
        operation_id='v1_admin_property_detail_retrieve',
        responses={'200': {'$ref': '#/components/schemas/AdminPropertyDetail'}}
    )
    def get(self, request, pk):
        from apps.properties.serializers import AdminPropertyDetailSerializer
        prop = get_object_or_404(Property, pk=pk)
        return Response(AdminPropertyDetailSerializer(prop, context={'request': request}).data)


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

    @extend_schema(
        tags=['Admin'], 
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by full name or email'),
            OpenApiParameter('account_status', OpenApiTypes.STR, enum=['active', 'inactive', 'suspend'], description='Filter by account status'),
        ],
        responses={'200': {'type': 'object', 'properties': {'count': {'type': 'integer'}, 'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/UserProfile'}}}}})
    def get(self, request):
        from apps.accounts.serializers import UserProfileSerializer
        from django.db.models import Q
        
        qs = User.objects.filter(role='buyer')
        
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(Q(full_name__icontains=search) | Q(email__icontains=search))
            
        account_status_filter = request.query_params.get('account_status')
        if account_status_filter == 'active':
            qs = qs.filter(is_active=True, is_banned=False)
        elif account_status_filter == 'inactive':
            qs = qs.filter(is_active=False)
        elif account_status_filter == 'suspend':
            qs = qs.filter(is_banned=True)
            
        qs = qs.order_by('-member_since')
        serializer = UserProfileSerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Admin'], operation_id='v1_admin_user_detail_retrieve', responses={'200': {'$ref': '#/components/schemas/UserProfile'}})
    def get(self, request, pk):
        from apps.accounts.serializers import UserProfileSerializer
        user = get_object_or_404(User, pk=pk)
        return Response(UserProfileSerializer(user).data)


class AdminUserBanView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(request=None, operation_id='v1_admin_user_ban', responses=AdminActionResponseSerializer, tags=['Admin'])
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

    @extend_schema(
        tags=['Admin'], 
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by full name, email, or brand name'),
            OpenApiParameter('verified_only', OpenApiTypes.BOOL, description='Filter for verified agents only'),
            OpenApiParameter('verify_list', OpenApiTypes.BOOL, description='Filter for verified agents only (alias for verified_only)'),
            OpenApiParameter('account_status', OpenApiTypes.STR, enum=['active', 'inactive', 'suspend'], description='Filter by account status'),
        ],
        responses={'200': {'type': 'object', 'properties': {'count': {'type': 'integer'}, 'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/UserProfile'}}}}})
    def get(self, request):
        from apps.accounts.serializers import UserProfileSerializer
        from django.db.models import Q
        
        qs = User.objects.filter(role='agent').select_related('agent_profile')
        
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) | 
                Q(email__icontains=search) | 
                Q(agent_profile__brand_name__icontains=search)
            )
            
        verified_only = request.query_params.get('verified_only') or request.query_params.get('verify_list')
        if verified_only == 'true':
            qs = qs.filter(agent_profile__is_verified=True)

        account_status_filter = request.query_params.get('account_status')
        if account_status_filter == 'active':
            qs = qs.filter(is_active=True, is_banned=False)
        elif account_status_filter == 'inactive':
            qs = qs.filter(is_active=False)
        elif account_status_filter == 'suspend':
            qs = qs.filter(is_banned=True)
            
        qs = qs.order_by('-member_since')
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

class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ('page_type', 'content')

class StaticPageView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = StaticPageSerializer

    @extend_schema(tags=['Admin Settings'], operation_id='v1_admin_static_page_retrieve', responses={'200': StaticPageSerializer})
    def get(self, request, page_type):
        page, _ = StaticPage.objects.get_or_create(page_type=page_type, defaults={'content': ''})
        return Response({'page_type': page.page_type, 'content': page.content})

    @extend_schema(tags=['Admin Settings'], operation_id='v1_admin_static_page_update', request=StaticPageSerializer, responses={'200': StaticPageSerializer})
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
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]
    
    @extend_schema(responses=PropertyTypeSerializer(many=True), tags=['Admin Settings'])
    def get(self, request):
        types = PropertyType2.objects.all()
        return Response(PropertyTypeSerializer(types, many=True).data)

    @extend_schema(request=PropertyTypeSerializer, responses=PropertyTypeSerializer, tags=['Admin Settings'])
    def post(self, request):
        from django.utils.text import slugify
        type_name = request.data.get('type', '').strip()
        if not type_name:
            return Response({'error': 'type required.'}, status=status.HTTP_400_BAD_REQUEST)
        obj, _ = PropertyType2.objects.get_or_create(name=type_name, defaults={'slug': slugify(type_name)})
        return Response(PropertyTypeSerializer(obj).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=PropertyTypeSerializer, responses=PropertyTypeSerializer, tags=['Admin Settings'])
    def patch(self, request):
        from django.utils.text import slugify
        obj_id = request.data.get('id')
        new_type = request.data.get('type', '').strip()
        if not obj_id or not new_type:
            return Response({'error': 'id and type required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        obj = get_object_or_404(PropertyType2, id=obj_id)
        obj.name = new_type
        obj.slug = slugify(new_type)
        obj.save()
        return Response(PropertyTypeSerializer(obj).data)

    @extend_schema(request=PropertyTypeSerializer, responses=OpenApiResponse(description="Deleted"), tags=['Admin Settings'])
    def delete(self, request):
        obj_id = request.data.get('id')
        if not obj_id:
             return Response({'error': 'id required.'}, status=status.HTTP_400_BAD_REQUEST)
        PropertyType2.objects.filter(id=obj_id).delete()
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
        from django.core.mail import send_mail
        from django.conf import settings

        msg = get_object_or_404(SupportMessage, pk=pk)
        reply_text = request.data.get('message', '')
        
        msg.reply = reply_text
        msg.is_replied = True
        msg.replied_at = timezone.now()
        msg.save()

        # Send email to user
        subject = 'Scan2Home — Support Reply'
        message = (
            f"Hello {msg.user.full_name},\n\n"
            f"An admin has replied to your support message:\n\n"
            f"Your Message: {msg.message}\n\n"
            f"Admin Reply: {reply_text}\n\n"
            f"Best regards,\nScan2Home Team"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[msg.user.email],
            fail_silently=True,
        )

        return Response({'message': 'Reply sent.'})
