import django_filters

from .models import Message


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message objects.

    Supports:
    - ?user=<user_uuid>                    → filter by sender (user)
    - ?from_date=YYYY-MM-DDTHH:MM         → messages sent at or after this datetime
    - ?to_date=YYYY-MM-DDTHH:MM           → messages sent at or before this datetime
    - ?conversation=<conversation_uuid>    → filter by conversation
    """

    user = django_filters.UUIDFilter(field_name="sender__user_id")
    from_date = django_filters.DateTimeFilter(
        field_name="sent_at",
        lookup_expr="gte",
    )
    to_date = django_filters.DateTimeFilter(
        field_name="sent_at",
        lookup_expr="lte",
    )
    conversation = django_filters.UUIDFilter(
        field_name="conversation__conversation_id"
    )

    class Meta:
        model = Message
        fields = ["user", "from_date", "to_date", "conversation"]
