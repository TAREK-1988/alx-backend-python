import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class UserRole(models.TextChoices):
    GUEST = "guest", "Guest"
    HOST = "host", "Host"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    """
    Custom user model with:
    - user_id (UUID primary key)
    - unique email (used for login)
    - role
    - optional phone_number
    - created_at timestamp
    """

    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Unused username field kept for backwards compatibility.",
    )
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.GUEST,
    )
    phone_number = models.CharField(
        max_length=32,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email + password only

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"


class Conversation(models.Model):
    """
    Conversation model:
    - conversation_id (UUID primary key)
    - participants (many-to-many User)
    - created_at timestamp
    """

    conversation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    participants = models.ManyToManyField(
        User,
        related_name="conversations",
        blank=False,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self) -> str:
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    Message model:
    - message_id (UUID primary key)
    - sender (FK to User)
    - conversation (FK to Conversation)
    - message_body (text)
    - sent_at timestamp
    """

    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
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
    sent_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self) -> str:
        preview = self.message_body[:30].replace("\n", " ")
        return f"{self.sender.email}: {preview}"

