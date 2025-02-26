from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for standardizing API pagination.

    Attributes:
        page_size (int): Default number of items per page (10).
        page_size_query_param (str): Allows clients to specify page size using the "page_size" query parameter.
        max_page_size (int): Maximum number of items allowed per page (100).
    """
    page_size = 10  # Default number of items per page
    page_size_query_param = "page_size"  # Query param to allow clients to set page size
    max_page_size = 100  # Restrict maximum page size to prevent performance issues
