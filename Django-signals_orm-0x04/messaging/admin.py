from django.contrib import admin

from .models import Message, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "short_content", "timestamp")
    list_filter = ("sender", "receiver", "timestamp")
    search_fields = ("content", "sender__username", "receiver__username")

    def short_content(self, obj: Message) -> str:
        """
        Helper to show a readable preview of the message content in the admin list.
        """
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content

    short_content.short_description = "Content"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message__content")

