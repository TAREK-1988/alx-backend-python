import os
from datetime import datetime

from django.conf import settings


class RequestLoggingMiddleware:
    """
    Middleware that logs each request with timestamp, user and path.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        log_file = getattr(settings, "REQUEST_LOG_FILE", "requests.log")
        self.log_file_path = os.path.join(settings.BASE_DIR, "Django-Middleware-0x03", log_file)

        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

    def __call__(self, request):
        user = request.user if hasattr(request, "user") and request.user.is_authenticated else "Anonymous"

        log_line = f"{datetime.now()} - User: {user} - Path: {request.path}\n"

        with open(self.log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_line)

        response = self.get_response(request)
        return response
