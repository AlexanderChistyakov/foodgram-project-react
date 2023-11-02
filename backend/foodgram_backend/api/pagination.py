from rest_framework.pagination import PageNumberPagination


class LimitedPagination(PageNumberPagination):
    page_size_query_param = 'limit'
