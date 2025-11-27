from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance: Message, created: bool, **kwargs) -> None:
    """
    Create a notification for the receiver whenever a new message is created.

    This keeps the side-effect (notification creation) decoupled from
    the core message creation logic.
    """
    if not created:
        # We only want to create a notification the first time the message is saved.
        return

    Notification.objects.create(
        user=instance.receiver,
        message=instance,
    )

