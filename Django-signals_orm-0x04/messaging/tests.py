from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Message, Notification

User = get_user_model()


class MessageNotificationSignalTests(TestCase):
    def setUp(self) -> None:
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="password123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="password123",
        )

    def test_notification_created_when_message_is_created(self):
        """
        A notification should be created for the receiver
        whenever a new message instance is created.
        """
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello from tests!",
        )

        notifications = Notification.objects.filter(user=self.receiver)
        self.assertEqual(notifications.count(), 1)

        notification = notifications.first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.message, msg)
        self.assertFalse(notification.is_read)

    def test_no_additional_notification_on_message_update(self):
        """
        Updating an existing message should NOT create a new notification.
        """
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial content",
        )
        # One notification created on initial save
        self.assertEqual(Notification.objects.filter(user=self.receiver).count(), 1)

        # Update the message
        msg.content = "Updated content"
        msg.save()

        # Still only one notification for that receiver/message
        self.assertEqual(Notification.objects.filter(user=self.receiver).count(), 1)

