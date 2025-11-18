from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    Pagination for messages.

    The API will return 20 messages per page by default.
    This is used both as the global DEFAULT_PAGINATION_CLASS
    and explicitly in the MessageViewSet.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
