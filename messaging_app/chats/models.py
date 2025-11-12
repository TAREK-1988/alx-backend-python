import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom user model.

    Fields coming from AbstractUser (kept / overridden):
      - first_name (NOT NULL)
      - last_name  (NOT NULL)
      - email      (unique, NOT NULL)
      - password   (hashed password)

    Extra fields required by the specification:
      - user_id    (UUID primary key, indexed)
      - phone_number (optional)
      - role       (guest, host, admin)
      - created_at (timestamp)
    """

    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    # Explicitly redefining these fields so they appear in this file
    # and match the specification (NOT NULL VARCHAR).
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    email = models.EmailField(
        unique=True,
    )

    phone_number = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )

    ROLE_CHOICES = (
        ("guest", "Guest"),
        ("host", "Host"),
        ("admin", "Admin"),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="guest",
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    # password_hash is handled by the inherited "password" field
    # from AbstractUser, which stores a hashed password.

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"


class Conversation(models.Model):
    """
    Conversation model.

    - conversation_id: UUID primary key
    - participants:    users taking part in the conversation
    - created_at:      timestamp
    """

    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    participants = models.ManyToManyField(
        User,
        related_name="conversations",
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    def __str__(self) -> str:
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    Message model.

    - message_id:   UUID primary key
    - sender:       FK to User(user_id)
    - conversation: FK to Conversation(conversation_id)
    - message_body: text body of the message
    - sent_at:      timestamp
    """

    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    message_body = models.TextField()

    sent_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    class Meta:
        ordering = ["sent_at"]

    def __str__(self) -> str:
        preview = self.message_body[:30].replace("\n", " ")
        return f"{self.sender.email}: {preview}"
