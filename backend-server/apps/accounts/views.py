from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    BuyerRegisterSerializer, AgentRegisterSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    VerifyOTPSerializer, ResetPasswordSerializer, LoginSerializer,
    AgentReviewSerializer
)
from .models import AgentProfile, AgentReview
from .services import AuthService
from apps.common.doc_examples import (
    BUYER_REGISTER_REQUEST, AGENT_REGISTER_REQUEST, LOGIN_REQUEST, LOGIN_RESPONSE
)

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
        }
    }


class BuyerRegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=BuyerRegisterSerializer,
        responses=OpenApiResponse(description="User registered successfully"),
        examples=[BUYER_REGISTER_REQUEST],
        tags=['Auth']
    )
    def post(self, request):
        serializer = BuyerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(get_tokens_for_user(user), status=status.HTTP_201_CREATED)


class AgentRegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=AgentRegisterSerializer,
        responses=OpenApiResponse(description="User registered successfully"),
        examples=[AGENT_REGISTER_REQUEST],
        tags=['Auth']
    )
    def post(self, request):
        serializer = AgentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(get_tokens_for_user(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses=OpenApiResponse(description="Login successful"),
        examples=[LOGIN_REQUEST, LOGIN_RESPONSE],
        tags=['Auth']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower().strip()
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_banned:
            return Response({'error': 'Your account has been banned.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(get_tokens_for_user(user))


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserProfileSerializer, tags=['Auth'])
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(request=UserProfileUpdateSerializer, responses=UserProfileSerializer, tags=['Auth'])
    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer, responses=OpenApiResponse(description="Password updated"), tags=['Auth'])
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password updated successfully.'})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=ForgotPasswordSerializer, responses=OpenApiResponse(description="OTP sent"), tags=['Auth'])
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if not User.objects.filter(email=email).exists():
            # Don't reveal if email exists
            return Response({'message': 'If this email is registered, you will receive an OTP.'})

        AuthService.send_otp(email)
        return Response({'message': 'OTP sent to your email.'})


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=VerifyOTPSerializer, responses=OpenApiResponse(description="OTP verified"), tags=['Auth'])
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_valid = AuthService.verify_otp(
            serializer.validated_data['email'],
            serializer.validated_data['otp_code']
        )
        if not is_valid:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'OTP verified.'})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=ResetPasswordSerializer, responses=OpenApiResponse(description="Password reset successfully"), tags=['Auth'])
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        is_valid = AuthService.verify_otp(data['email'], data['otp_code'])
        if not is_valid:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=data['email'])
            user.set_password(data['new_password'])
            user.save()
            return Response({'message': 'Password reset successfully.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=OpenApiResponse(description="Account deleted"), tags=['Auth'])
    def delete(self, request):
        user = request.user
        # Soft delete — deactivate instead of hard delete
        user.is_active = False
        user.save()
        return Response({'message': 'Account deleted.'}, status=status.HTTP_204_NO_CONTENT)


class AgentRateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AgentReviewSerializer,
        responses=AgentReviewSerializer,
        tags=['Agents']
    )
    def post(self, request, agent_id):
        # agent_id is the user ID of the agent
        agent_profile = get_object_or_404(AgentProfile, user__id=agent_id)
        
        # Check if user already reviewed this agent
        review = AgentReview.objects.filter(user=request.user, agent=agent_profile).first()
        
        serializer = AgentReviewSerializer(review, data=request.data, partial=bool(review))
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, agent=agent_profile)
        
        return Response(
            serializer.data, 
            status=status.HTTP_200_OK if review else status.HTTP_201_CREATED
        )
