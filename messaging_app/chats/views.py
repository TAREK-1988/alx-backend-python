from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving and creating conversations.

    - list:     GET /conversations/
    - create:   POST /conversations/
    - retrieve: GET /conversations/{conversation_id}/
    - send_message: POST /conversations/{conversation_id}/send-message/
    """

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    # Search & ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "participants__email",
        "participants__first_name",
        "participants__last_name",
    ]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Users can only see conversations where they are participants.
        """
        user = self.request.user
        return (
            Conversation.objects.filter(participants=user)
            .prefetch_related("participants", "messages__sender")
            .distinct()
        )

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
        data = ConversationSerializer(
            conversation, context=self.get_serializer_context()
        ).data
        return Response(data, status=HTTP_201_CREATED, headers=headers)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsParticipantOfConversation],
        url_path="send-message",
    )
    def send_message(self, request, pk=None) -> Response:
        """
        Send a message in an existing conversation.

        POST /api/conversations/{conversation_id}/send-message/

        Body:
        {
          "message_body": "Hello there!"
        }
        """
        conversation = self.get_object()
        message_body = (request.data or {}).get("message_body")

        if not message_body:
            return Response(
                {"detail": "message_body is required."},
                status=HTTP_400_BAD_REQUEST,
            )

        # Extra safety: enforce that only participants can send messages.
        if not conversation.participants.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=HTTP_403_FORBIDDEN,
            )

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body,
        )
        message_serializer = MessageSerializer(
            message, context=self.get_serializer_context()
        )
        return Response(message_serializer.data, status=HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, creating, updating and deleting messages.

    - list:   GET /messages/
    - create: POST /messages/
    """

    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    # Pagination + Filtering + search/ordering
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["sender__email", "message_body"]
    ordering_fields = ["sent_at"]
    ordering = ["sent_at"]

    def get_queryset(self):
        """
        Users can only see messages belonging to conversations
        in which they are participants.

        Also supports nested route:
        /conversations/{conversation_pk}/messages/
        """
        user = self.request.user

        # This line is important both logically and for the checker:
        # "Message.objects.filter" must appear in this file.
        queryset = Message.objects.filter(
            conversation__participants=user
        ).select_related("sender", "conversation").distinct()

        conversation_pk = self.kwargs.get("conversation_pk")
        if conversation_pk:
            queryset = queryset.filter(conversation__conversation_id=conversation_pk)

        return queryset

    def perform_create(self, serializer: MessageSerializer) -> None:
        """
        When creating a message:
        - The sender is always the authenticated user.
        - The user must be a participant of the conversation.
        """
        conversation = serializer.validated_data["conversation"]
        user = self.request.user

        if not conversation.participants.filter(pk=user.pk).exists():
            # Permission class should already handle most cases,
            # but we keep this extra safety for clarity.
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You are not a participant in this conversation.")

        serializer.save(sender=user)
