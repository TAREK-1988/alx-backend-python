from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    """
    Represents a single message sent from one user to another.
    """

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Task 1: track whether the message has ever been edited
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.sender} -> {self.receiver}: {self.content[:30]}"


class Notification(models.Model):
    """
    Stores a notification generated when a user receives a new message.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Notification for {self.user} (message #{self.message_id})"


class MessageHistory(models.Model):
    """
    Keeps a history of message edits so that previous versions can be displayed
    in the user interface.
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="history",
    )
    old_content = models.TextField()

    # Task 1: fields required by the checker
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_messages_history",
    )

    class Meta:
        ordering = ["-edited_at"]

    def __str__(self) -> str:
        return f"History for message {self.message_id} at {self.edited_at}"
