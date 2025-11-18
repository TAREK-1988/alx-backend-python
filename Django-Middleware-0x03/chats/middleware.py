from datetime import datetime
from pathlib import Path

from django.conf import settings


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file_path = Path(settings.BASE_DIR) / "requests.log"

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            user_repr = str(user)
        else:
            user_repr = "Anonymous"

        log_line = f"{datetime.now()} - User: {user_repr} - Path: {request.path}\n"

        try:
            with self.log_file_path.open("a", encoding="utf-8") as log_file:
                log_file.write(log_line)
        except OSError:
            # Fail silently if the log file cannot be written
            pass

        response = self.get_response(request)
        return response
