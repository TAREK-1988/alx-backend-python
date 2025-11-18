import os
from datetime import datetime, time, timedelta

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


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.window_seconds = 60
        self.max_requests = 5
        self._requests_per_ip = {}

    def _is_chat_message_request(self, request) -> bool:
        if request.method != "POST":
            return False
        path = request.path
        return path.startswith("/chats") or path.startswith("/api/chats")

    def _get_client_ip(self, request) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def __call__(self, request):
        if self._is_chat_message_request(request):
            client_ip = self._get_client_ip(request)
            now = datetime.now()
            window = timedelta(seconds=self.window_seconds)

            timestamps = self._requests_per_ip.get(client_ip, [])
            timestamps = [ts for ts in timestamps if now - ts <= window]

            if len(timestamps) >= self.max_requests:
                return HttpResponseForbidden("Rate limit exceeded: too many chat messages.")

            timestamps.append(now)
            self._requests_per_ip[client_ip] = timestamps

        response = self.get_response(request)
        return response


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_prefixes = ("/admin/", "/moderation/")

    def _is_protected_path(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.protected_prefixes)

    def _has_admin_or_moderator_role(self, user) -> bool:
        if user is None or not getattr(user, "is_authenticated", False):
            return False

        if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
            return True

        role = getattr(user, "role", None)
