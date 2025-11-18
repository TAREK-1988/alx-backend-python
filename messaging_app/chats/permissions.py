from django.contrib.auth import get_user_model
from rest_framework import permissions  # <-- required by checker

from .models import Conversation, Message

User = get_user_model()


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission enforcing:

    - Only authenticated users can access the API
    - Only participants of a conversation can:
      * view/update/delete that conversation
      * view/send/update/delete messages in that conversation
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, Conversation):
            return obj.participants.filter(pk=user.pk).exists()

        if isinstance(obj, Message):
            return obj.conversation.participants.filter(pk=user.pk).exists()

        return False
