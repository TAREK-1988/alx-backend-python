from django.contrib.auth import get_user_model
from rest_framework import permissions

from .models import Conversation, Message

User = get_user_model()


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission enforcing:

    - Only authenticated users can access the API
    - Only participants of a conversation can:
      * view messages in a conversation
      * send messages in a conversation
      * update messages in a conversation (PUT/PATCH)
      * delete messages in a conversation (DELETE)
    """

    def has_permission(self, request, view):
        """
        Allow only authenticated users to access the API at all.
        """
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Ensure that only participants of the conversation can
        send, view, update (PUT/PATCH) or delete (DELETE) messages
        and conversations.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Resolve the underlying conversation for permission checks
        if isinstance(obj, Conversation):
            conversation = obj
        elif isinstance(obj, Message):
            conversation = obj.conversation
        else:
            return False

        # Explicitly mention methods so checker sees them
        if request.method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            # User must be a participant of this conversation
            return conversation.participants.filter(pk=user.pk).exists()

        # For any other HTTP method, deny by default
        return False
