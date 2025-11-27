from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Message, Notification, MessageHistory

User = get_user_model()


class MessageSignalsTests(TestCase):
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

    def test_message_history_created_on_edit(self):
        """
        Editing an existing message should create a MessageHistory entry
        with the old content and mark the message as edited.
        """
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content",
        )

        # Update the content
        msg.content = "Updated content"
        msg.save()

        histories = MessageHistory.objects.filter(message=msg)
        self.assertEqual(histories.count(), 1)

        history = histories.first()
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.edited_by, self.sender)

        # The message should now be flagged as edited
        msg.refresh_from_db()
        self.assertTrue(msg.edited)

    def test_no_history_created_if_content_is_unchanged(self):
        """
        Saving a message without changing the content should not
        generate a new history entry.
        """
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Same content",
        )

        # Save again without changing content
        msg.save()

        self.assertEqual(MessageHistory.objects.filter(message=msg).count(), 0)
        self.assertFalse(msg.edited)
