import logging
from pathlib import Path
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone


logger = logging.getLogger("chats.request_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    log_file_path = Path(settings.BASE_DIR) / "requests.log"
    file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class RequestLoggingMiddleware:
    """
    Logs each incoming request with timestamp, user and path
    to the requests.log file at the project root.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            user_repr = str(user)
        else:
            user_repr = "Anonymous"

        now = timezone.now().isoformat()
        log_message = f"{now} - User: {user_repr} - Path: {request.path}"
        logger.info(log_message)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """
    Restricts access to chat-related endpoints outside a specific time window.
    Chat is only available between 09:00 and 18:00 server local time.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.start_hour = 9
        self.end_hour = 18

    def _is_chat_path(self, path: str) -> bool:
        prefixes = (
            "/chats/",
            "/api/chats/",
            "/api/messages",
            "/api/conversations",
        )
        return any(path.startswith(prefix) for prefix in prefixes)

    def __call__(self, request):
        if self._is_chat_path(request.path):
            now = timezone.localtime(timezone.now())
            current_hour = now.hour
            if not (self.start_hour <= current_hour < self.end_hour):
                return HttpResponseForbidden(
                    "Chat is only available between 09:00 and 18:00."
                )

        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    """
    Simple rate-limiting middleware based on client IP.
    Limits the number of POST chat messages to max_requests
    within a sliding time window.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.window_seconds = 60
        self.max_requests = 5

    def _is_chat_message_request(self, request) -> bool:
        if request.method != "POST":
            return False
        prefixes = (
            "/chats/",
            "/api/chats/",
            "/api/messages",
            "/api/conversations",
        )
        return any(request.path.startswith(prefix) for prefix in prefixes)

    def _get_client_ip(self, request) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def __call__(self, request):
        if self._is_chat_message_request(request):
            client_ip = self._get_client_ip(request)
            cache_key = f"chat_rate_limit:{client_ip}"
            now = timezone.now()

            timestamps = cache.get(cache_key, [])
            timestamps = [
                ts for ts in timestamps
                if (now - ts) <= timedelta(seconds=self.window_seconds)
            ]
            timestamps.append(now)

            if len(timestamps) > self.max_requests:
                return JsonResponse(
                    {"detail": "Rate limit exceeded. Please try again later."},
                    status=429,
                )

            cache.set(cache_key, timestamps, timeout=self.window_seconds)

        response = self.get_response(request)
        return response


class RolepermissionMiddleware:
    """
    Enforces role-based access control for protected paths.
    Only users with admin or moderator role are allowed.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_prefixes = ("/admin/", "/moderation/")

    def _is_protected_path(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.protected_prefixes)

    def _has_admin_or_moderator_role(self, user) -> bool:
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
            return True

        role = getattr(user, "role", None)
        if isinstance(role, str) and role.lower() in {"admin", "moderator"}:
            return True

        if hasattr(user, "groups"):
            if user.groups.filter(name__in=["admin", "moderator"]).exists():
                return True

        return False

    def __call__(self, request):
        if self._is_protected_path(request.path):
            user = getattr(request, "user", None)
            if not self._has_admin_or_moderator_role(user):
                return HttpResponseForbidden(
                    "You do not have permission to access this resource."
                )

        response = self.get_response(request)
        return response
