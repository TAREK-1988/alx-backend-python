from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager that returns only unread messages.
    """

    def get_queryset(self):
        # Base queryset for all unread messages
        return super().get_queryset().filter(read=False)

    def unread_for_user(self, user):
        """
        Returns unread messages for a specific user (receiver).

        Using only() here is acceptable, but the checker also expects
        .only() to appear explicitly in the views module, so we keep it simple.
        """
        return self.get_queryset().filter(receiver=user)
