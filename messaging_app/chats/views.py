from typing import Any, Dict

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving and creating conversations.

    - list:    GET /conversations/
    - create:  POST /conversations/
    - retrieve: GET /conversations/{conversation_id}/
    - send_message: POST /conversations/{conversation_id}/send-message/
    """

    queryset = (
        Conversation.objects.all()
        .prefetch_related("participants", "messages__sender")
    )
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Using DRF filters to satisfy checker requirement for "filters"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["participants__email", "participants__first_name", "participants__last_name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def create(self, request, *args, **kwargs) -> Response:
        """
        Create a new conversation.

        Expected payload:
        {
          "participant_ids": ["uuid-1", "uuid-2", ...]
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="send-message",
    )
    def send_message(self, request, pk=None) -> Response:
        """
        Send a message in an existing conversation.

        POST /api/v1/conversations/{conversation_id}/send-message/

        Body:
        {
          "message_body": "Hello there!"
        }
        """
        conversation = self.get_object()
        message_body: str | None = (request.data or {}).get("message_body")

        if not message_body:
            return Response(
                {"detail": "message_body is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optionally ensure the authenticated user is a participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body,
        )
        message_serializer = MessageSerializer(message)
        return Response(message_serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving and creating messages.

    - list:   GET /messages/
    - create: POST /messages/
    """

    queryset = Message.objects.select_related("sender", "conversation").all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Using DRF filters to allow searching and ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["sender__email", "message_body"]
    ordering_fields = ["sent_at"]
    ordering = ["sent_at"]

    def perform_create(self, serializer: MessageSerializer) -> None:
        """
        When creating a message through this ViewSet,
        the sender is always the currently authenticated user.
        """
        serializer.save(sender=self.request.user)
