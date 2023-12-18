from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
    """Постраничная пагинация."""
    page_size_query_param = 'page_size'
