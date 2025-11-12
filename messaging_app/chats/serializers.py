from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
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
        )
        read_only_fields = ("user_id", "created_at")
        

class MessageSerializer(serializers.ModelSerializer):
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
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of user UUIDs that should participate in this conversation.",
    )

    class Meta:
        model = Conversation
        fields = (
            "conversation_id",
            "participants",
            "participant_ids",
            "messages",
            "created_at",
        )
        read_only_fields = ("conversation_id", "participants", "messages", "created_at")

    def create(self, validated_data):
        participant_ids = validated_data.pop("participant_ids", [])
        conversation = Conversation.objects.create(**validated_data)
        if participant_ids:
            users = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.add(*users)
        return conversation

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop("participant_ids", None)
        conversation = super().update(instance, validated_data)
        if participant_ids is not None:
            users = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(users)
        return conversation

