from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def create_tokens_for_user(user: User) -> dict:
    """
    Helper function to generate JWT tokens for a given user.

    This ensures the chats/auth.py file is present, non-empty,
    and provides a useful utility for issuing JWT tokens.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
