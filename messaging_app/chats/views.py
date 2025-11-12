from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsSenderOrReadOnly


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving and creating conversations.

    Extra actions:
    - send_message: send a new message in a given conversation.
    """

    queryset = (
        Conversation.objects.all()
        .prefetch_related("participants", "messages__sender")
    )
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="send-message",
    )
    def send_message(self, request, pk=None):
        """
        POST /api/v1/conversations/{conversation_id}/send-message/

        Request body:
        {
          "message_body": "Hello!"
        }
        """
        conversation = self.get_object()
        message_body = (request.data or {}).get("message_body")

        if not message_body:
            return Response(
                {"detail": "message_body is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure the current user is a participant
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
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving and creating messages.

    The sender is always the currently authenticated user.
    """

    queryset = Message.objects.select_related("sender", "conversation").all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsSenderOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

