from rest_framework.pagination import PageNumberPagination


class UserApiPagination(PageNumberPagination):
    page_size = 1
