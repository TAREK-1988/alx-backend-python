from django.contrib import admin

from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "short_content", "timestamp", "edited")
    list_filter = ("sender", "receiver", "timestamp", "edited")
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


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "edited_by", "edited_at", "short_old_content")
    list_filter = ("edited_at", "edited_by")
    search_fields = ("old_content", "edited_by__username", "message__content")

    def short_old_content(self, obj: MessageHistory) -> str:
        return (obj.old_content[:50] + "...") if len(obj.old_content) > 50 else obj.old_content

    short_old_content.short_description = "Old content"
