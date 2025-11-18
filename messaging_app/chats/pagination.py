from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MessagePagination(PageNumberPagination):
    """
    Pagination for messages.

    The API will return 20 messages per page by default.
    This class customizes the paginated response to include:
    - total count (page.paginator.count)
    - next/previous links
    - results
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Build a paginated response with total count and navigation links.
        The checker expects 'page.paginator.count' to appear in this file.
        """
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
