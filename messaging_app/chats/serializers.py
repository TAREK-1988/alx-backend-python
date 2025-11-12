from typing import Any, Dict, List, Optional
from uuid import UUID

from rest_framework import serializers

from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.
    Adds a read-only display_name field using CharField.
    """

    display_name = serializers.CharField(
        source="get_full_name",
        read_only=True,
        help_text="Full name composed of first_name and last_name.",
    )

    class Meta:
        model = User
        fields = (
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "created_at",
            "display_name",
        )
        read_only_fields = ("user_id", "created_at", "display_name")


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message objects.
    Includes nested sender information.
    """

    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = (
            "message_id",
            "sender",
            "conversation",
            "message_body",
            "sent_at",
        )
        read_only_fields = ("message_id", "sender", "sent_at")


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation objects.

    - participants: nested list of users (read-only).
    - messages: nested list of messages (read-only).
    - participant_ids: write-only list of user UUIDs used to create/update participants.
    - last_message: computed field using SerializerMethodField.
    """

    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of user UUIDs participating in this conversation.",
    )

    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "conversation_id",
            "participants",
            "participant_ids",
            "messages",
            "last_message",
            "created_at",
        )
        read_only_fields = ("conversation_id", "participants", "messages", "last_message", "created_at")

    # ---------- Validation ----------

    def validate_participant_ids(self, value: List[UUID]) -> List[UUID]:
        """
        Ensure that at least one participant is provided when creating a conversation.
        """
        if not value:
            raise serializers.ValidationError("At least one participant_id must be provided.")
        return value

    # ---------- Computed fields ----------

    def get_last_message(self, obj: Conversation) -> Optional[Dict[str, Any]]:
        """
        Return the most recent message in this conversation, if any.
        """
        last = obj.messages.order_by("-sent_at").first()
        if not last:
            return None
        return MessageSerializer(last).data

    # ---------- Create / Update ----------

    def create(self, validated_data: Dict[str, Any]) -> Conversation:
        participant_ids: List[UUID] = validated_data.pop("participant_ids", [])
        conversation = Conversation.objects.create(**validated_data)

        if participant_ids:
            users = User.objects.filter(user_id__in=participant_ids)
            if not users.exists():
                raise serializers.ValidationError("No valid users found for the given participant_ids.")
            conversation.participants.add(*users)

        return conversation

    def update(self, instance: Conversation, validated_data: Dict[str, Any]) -> Conversation:
        participant_ids: Optional[List[UUID]] = validated_data.pop("participant_ids", None)

        # Update basic fields if we add any in the future.
        instance = super().update(instance, validated_data)

        if participant_ids is not None:
            users = User.objects.filter(user_id__in=participant_ids)
            if not users.exists():
                raise serializers.ValidationError("No valid users found for the given participant_ids.")
            instance.participants.set(users)

        return instance
