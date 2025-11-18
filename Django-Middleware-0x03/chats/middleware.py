import os
from datetime import datetime, time

from django.conf import settings
from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        log_file = getattr(settings, "REQUEST_LOG_FILE", "requests.log")
        self.log_file_path = os.path.join(settings.BASE_DIR, log_file)

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            user_repr = str(user)
        else:
            user_repr = "Anonymous"

        log_line = f"{datetime.now()} - User: {user_repr} - Path: {request.path}\n"

        try:
            with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_line)
        except OSError:
            pass

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.start_closed = time(21, 0)  # 9 PM
        self.end_closed = time(6, 0)     # 6 AM

    def _is_chat_path(self, path: str) -> bool:
        return path.startswith("/chats") or path.startswith("/api/chats")

    def __call__(self, request):
        if self._is_chat_path(request.path):
            now = datetime.now().time()
            if now >= self.start_closed or now < self.end_closed:
                return HttpResponseForbidden("Chat is not available between 9PM and 6AM.")

        response = self.get_response(request)
        return response
