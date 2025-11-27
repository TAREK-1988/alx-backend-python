from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "messaging"

    def ready(self) -> None:
        """
        Import signal handlers so they are registered
        when the application is loaded.
        """
        # Importing inside ready() avoids side effects at import time.
        from . import signals  # noqa: F401

