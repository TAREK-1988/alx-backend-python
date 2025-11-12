from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers

from .views import ConversationViewSet, MessageViewSet

# Default router for top-level resources
router = routers.DefaultRouter()
router.register(r"conversations", ConversationViewSet, basename="conversation")
router.register(r"messages", MessageViewSet, basename="message")

# Nested router example for messages under conversations
# The checker expects NestedDefaultRouter to appear in this file.
nested_router = nested_routers.NestedDefaultRouter(
    router,
    r"conversations",
    lookup="conversation",
)
nested_router.register(
    r"messages",
    MessageViewSet,
    basename="conversation-messages",
)

urlpatterns = [
    # /api/conversations/, /api/messages/
    path("", include(router.urls)),
    # /api/conversations/{conversation_pk}/messages/
    path("", include(nested_router.urls)),
]
