import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from drf_spectacular.utils import extend_schema

from .serializers import ChatMessageSerializer, ChatResponseSerializer


class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChatMessageSerializer, responses=ChatResponseSerializer, tags=['Chat'])
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message'].strip()

        try:
            response = requests.post(
                settings.CHATBOT_SERVICE_URL,
                json={'message': message, 'user_id': str(request.user.id)},
                timeout=15,
            )
            response.raise_for_status()
            return Response(response.json())
        except requests.exceptions.ConnectionError:
            # Fallback FAQ response
            return Response({
                'reply': 'Our AI assistant is currently unavailable. Please contact support at support@scan2home.com or try again later.',
                'fallback': True,
            })
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
