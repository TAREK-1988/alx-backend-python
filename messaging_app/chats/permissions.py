from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSenderOrReadOnly(BasePermission):
    """
    Allow read-only access to any request.
    Allow write access only to the message sender.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "sender_id", None) == getattr(request.user, "user_id", None)

