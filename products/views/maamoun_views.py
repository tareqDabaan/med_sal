from rest_framework import decorators, generics
from rest_framework import permissions, status
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector, SearchQuery
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, Avg, Min, Max
from django.contrib.gis.geos import Point
from django.http import HttpRequest

from collections import defaultdict
from functools import reduce
from typing import Any

from products.file_handler import UploadImages, DeleteFiles
from products import permissions as local_permissions
from products import models, serializers

from core.pagination_classes.nine_element_paginator import CustomPagination
from utils.catch_helper import catch
from notification.models import Notification



class AllProducts(generics.ListAPIView):
    """
        An api that lists all products
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def list(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, language=language)
        return Response(serializer.data)


class CreateProduct(generics.CreateAPIView):
    """
        An api that allows to add products 
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def create(self, request, *args, **kwargs):
        new_file_names = self._upload_images(request)
        request.data["images"] = new_file_names
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , en_content="a new product added to your specified location"
            , ar_content="تم إضافة منتج جديد للفرع المحدد")
        
        return Response(resp.data, status=resp.status_code)
    
    def _upload_images(self, request):
        file_manager = UploadImages(request)
        return file_manager.upload_files("products", request.FILES.getlist("images"))


class RUDProduct(generics.RetrieveUpdateDestroyAPIView):
    """
        An api that allows to Read, Update and Delete a specific product 
        product ID is required 
    """
    permission_classes = (local_permissions.HasPermissionOrReadOnly, )
    serializer_class = serializers.ProudctSerializer
    queryset = models.Product.objects
    
    def retrieve(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        
        instance = self.get_object()
        serializer = self.get_serializer([instance], many=True, language=language)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        language = request.META.get("Accept-Language")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        if request.data.get("images"):
            # first delete old ones
            DeleteFiles().delete_files(instance.images)
            # then upload new ones and change names
            file_manager = UploadImages(request)
            data["images"] = file_manager.upload_files("products", request.FILES.getlist("images"))
            
        serializer = self.get_serializer(instance, data=data, partial=partial, language=language)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , en_content="product information edited"
            , ar_content="تم تعديل معلومات المنتج")
        
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        DeleteFiles().delete_files(instance.images)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=self.request.user.email, receiver_type="Service_Provider"
            , en_content="the product deleted"
            , ar_content="تم حذف المنتج")
        
        instance.delete()


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_category(request: HttpRequest, pk: int):
    """
    get all products for specific category
    pk here is category_id
    for everybody
    """
    language = request.META.get("Accept-Language")
    queryset = models.Product.objects.filter(service_provider_location__service_provider__category=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_location(request: HttpRequest, pk: int):
    """
    get all products for specific location
    pk here is location_id
    for everybody
    """
    language = request.META.get("Accept-Language")
    queryset = models.Product.objects.filter(service_provider_location=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_provider(request: HttpRequest, pk: int):
    """
    get all products for specific service provider
    pk here is service_provider_id
    for everybody
    """
    language = request.META.get("Accept-Language")
    queryset = models.Product.objects.filter(service_provider_location__service_provider=pk)
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def category_products_by_name(request: HttpRequest, category_name: str):
    language = request.META.get("Accept-Language")
    main_q = "service_provider_location__service_provider__category__"
    
    search_terms = category_name.split("_")
    search_exprs = (Q(search=SearchQuery(word)) for word in search_terms)
    search_func = reduce(lambda x, y: x | y, search_exprs)
    
    queryset = models.Product.objects.annotate(
        search=SearchVector(f"{main_q}en_name", f"{main_q}ar_name")).filter(search_func)
    
    if not queryset.exists():
        return Response({"message": "No products found relates to this category name"}
                    , status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def products_price_range(request: HttpRequest):
    language = request.META.get("Accept-Language")
    min_price, max_price = int(request.query_params["min_price"]), int(request.query_params["max_price"])
    
    queryset = models.Product.objects.filter(price__range=(min_price, max_price))
    if not queryset.exists():
        return Response({
            "message": "No products found within this range"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ProudctSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_products_statistics(request: HttpRequest, provider_id: int):
    # all_cat = Category.objects.annotate(num_of_services=Count("services", filter=Q(services__gt=1)))
    # for cat in all_cat: cat.id, cat.ar_name, cat.en_name, cat.num_services
    """
    number of services for each categories available in specific provider
    returns {category_id, category_name, services_count}
    """
    queryset = models.Product.objects.filter(service_provider_location__service_provider=provider_id)
    prices = queryset.aggregate(min_price=Min("price"), max_price=Max("price"))
    
    def sizing_rates():
        # first we filtered the provider services
        # then we aggregate similar services and find it's average rate
        queryset = models.ProductRates.objects.filter(
        product__service_provider_location__service_provider=provider_id).values(
            "product").annotate(avg_rate=Avg("rate"))
        
        limits = { (4.5, 5): 5, (3.5, 4.5): 4, (2.5, 3.5): 3, (1.5, 2.5): 2, (0.5, 1.5): 1, (0, 0.5): 0 }
        rates = defaultdict(int)
        
        for query in queryset:
            for limit in limits:
                if query["avg_rate"] >= limit[0] and query["avg_rate"] < limit[1]:
                    rates[limits[limit]] += 1
                    break
        
        return rates
    
    data = {}
    
    data["prices"] = {"min_price": prices["min_price"], "max_price": prices["max_price"]}
    data["rates"] = sizing_rates()
    
    return Response(data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def multiple_filters(request: HttpRequest):
    """
    query_params = {rates: list[numbers], min_price: number, max_price: number
                    , categories: list[numbers], }
    """
    language = request.META.get("Accept-Language")
    params = request.query_params
    
    q_expressions = set()
    callables = (check_range, check_category)
    for func in callables:
        q_expressions.add(func(params))
    
    q_expressions.discard(None)
    
    q_expressions, queryset = check_distance(params=params, q_expressions=q_expressions)
    queryset = check_rate(params, queryset)
    
    paginator = CustomPagination()
    list_products = paginator.paginate_queryset(queryset, request)
    
    serializer = serializers.ProudctSerializer(list_products, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_distance(params: dict[str, Any], q_expressions: set):
    longitude, latitude = params.get("logitude"), params.get("latitude")
    if longitude and latitude:
        longitude, latitude = float(longitude), float(latitude)
        location = Point(longitude, latitude)
        q_exp=Q(service_provider_location__location__distance_lt=(location, 1000000))
        q_expressions.add(q_exp)
        
        queryset = models.Product.objects.annotate(
            distance=Distance("service_provider_location__location", location)
                ).order_by("distance")
    
    else:
        queryset = models.Product.objects
    
    return q_expressions, queryset

def check_category(params: dict[str, Any]):
    """
    helper function for multiple filters api function
    """
    q_exp = None
    category_ids = params.get("categories", None)
    if category_ids:
        new_category_ids = catch(category_ids)
        
        q_exp = (Q(category__id=int(x)) for x in new_category_ids)
        q_exp = reduce(lambda a, b: a | b, q_exp)
    
    return q_exp

def check_range(params: dict[str, Any]):
    """
    helper function for multiple filters api function
    """
    q_exp = None
    min_price, max_price = params.get("min_price", None), params.get("max_price", None)
    if min_price and max_price:
        min_price, max_price = float(min_price), float(max_price)
        q_exp = Q(price__range=(min_price, max_price))
    
    return q_exp

def check_rate(params: dict[str, None], products_queryset):
    """
    helper function for multiple filters api function
    """
    rates = params.get("rates", None)
    if not rates:
        return products_queryset
    
    rates = catch(rates)
    
    new_products = []
    for product in products_queryset:
        avg_product_rate = product.product_rates.aggregate(Avg("rate", default=0))["rate__avg"]
        for rate in rates:
            if rate-0.5 <= avg_product_rate <= rate+0.5:
                new_products.append(product)
                break
    
    return new_products
