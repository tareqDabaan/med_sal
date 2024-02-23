from rest_framework.pagination import PageNumberPagination

from django.db.models import QuerySet
from django.http import HttpRequest



class CustomPagination(PageNumberPagination):
    page_size = 9


def custom_pagination_function(page_size: int):
    paginator = CustomPagination()
    paginator.page_size = page_size
    return paginator
