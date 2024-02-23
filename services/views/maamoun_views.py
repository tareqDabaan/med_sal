from rest_framework import generics, decorators
from rest_framework.response import Response
from rest_framework import status

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, Avg, QuerySet
from django.db.models import Avg, Min, Max
from django.contrib.gis.geos import Point
from django.http import HttpRequest

from collections import defaultdict
from functools import reduce
from typing import Any

from services import models, serializers, helpers

from products.file_handler import UploadImages, DeleteFiles
from notification.models import Notification

from utils.permission import HasPermission
from utils.catch_helper import catch

from core.pagination_classes.nine_element_paginator import custom_pagination_function


#
class CreateService(generics.CreateAPIView, helpers.FileMixin):
    serializer_class = serializers.CreateServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def create(self, request: HttpRequest, *args, **kwargs):
        image_objs = request.FILES.getlist("image")
        upload_images = UploadImages(request)
        images_names = upload_images.upload_files("services", image_objs)
        
        request.data["image"] = images_names
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , ar_content="تم إضافة خدمة جديدة إلى خدماتك"
            , en_content="A new service added to your sevices")
        
        return Response(resp.data, status=resp.status_code)

#
class ServiceRUD(generics.RetrieveUpdateDestroyAPIView, helpers.FileMixin):
    serializer_class = serializers.RUDServicesSerializer
    permission_classes = (HasPermission, )
    queryset = models.Service.objects
    
    def get_permissions(self):
        return [permission("service") for permission in self.permission_classes]
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        return super().get_serializer(*args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        delete_files = DeleteFiles()
        delete_files.delete_files(instance.image)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=self.request.user.email, receiver_type="Service_Provider"
            , ar_content="تم حذف الخدمة"
            , en_content="service has been deleted")
        
        return super().perform_destroy(instance)
    
    def update(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if request.data.get("image"):
            image_objs = request.FILES.getlist("image")
            upload_images = UploadImages(request)
            images_names = upload_images.upload_files("services", image_objs)
            
            request.data["image"] = images_names
            
            delete_files = DeleteFiles()
            delete_files.delete_files(instance.image)
            
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        Notification.objects.create(
            sender="system", sender_type="System"
            , receiver=request.user.email, receiver_type="Service_Provider"
            , ar_content="تم تعديل الخدمة"
            , en_content="service has been updated")
        
        return Response(serializer.data)

#
class ListAllServices(generics.ListAPIView):
    serializer_class = serializers.RUDServicesSerializer
    queryset = models.Service.objects
    permission_classes = ( )
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        return super().get_serializer(*args, **kwargs)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_services(request: HttpRequest, provider_id: int= None):
    """
    return services for specific provider
    """
    provider_id = provider_id or request.user.id
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(provider_location__service_provider=provider_id)
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 
@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_services_by_category(request: HttpRequest, provider_id: int):
    # all_cat = Category.objects.annotate(num_of_services=Count("services", filter=Q(services__gt=1)))
    # for cat in all_cat: cat.id, cat.ar_name, cat.en_name, cat.num_services
    """
    number of services for each categories available in specific provider
    returns {category_id, category_name, services_count}
    """
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(provider_location__service_provider=provider_id)
    prices = queryset.aggregate(min_price=Min("price"), max_price=Max("price"))
    
    def categories(queryset):
        frequencies = defaultdict(int)
        for query in queryset:
            category_id = query.category.id
            category_name = query.category.en_name if language == "en" else query.category.ar_name 
            
            frequencies[(category_id, category_name)] += 1
            
        def serialize_data(frequencies: defaultdict[tuple[int, str], int]):
            data = []
            for k, v in frequencies.items():
                data.append({"category_id": k[0], "category_name": k[1], "services_count": v})
            
            return data
        
        return serialize_data(frequencies)
    
    def sizing_rates():
        # first we filtered the provider services
        # then we aggregate similar services and find it's average rate
        queryset = models.ServiceRates.objects.filter(
        service__provider_location__service_provider=provider_id).values(
            "service").annotate(avg_rate=Avg("rate"))
        
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
    data["categories"] = categories(queryset)
    data["rates"] = sizing_rates()
    
    return Response(data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def provider_category_services(request: HttpRequest, provider_id: int, category_id: int):
    """
    return category related services for a specific provider
    """
    language = request.META.get("Accept-Language")
    queryset = models.Service.objects.filter(
        provider_location__service_provider=provider_id, category=category_id)
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def category_services_by_name(request: HttpRequest, category_name: str):
    """
    return services for specific category by category name
    """
    language = request.META.get("Accept-Language")
    
    search_terms = category_name.split("_")
    search_terms = (Q(search=SearchQuery(word)) for word in search_terms)
    search_func = reduce(lambda x, y : x | y, search_terms)
    
    queryset = models.Service.objects.annotate(
        search=SearchVector("category__en_name", "category__ar_name")).filter(search_func)
    
    if not queryset.exists():
        return Response({"message": "No services found relates to this category"}
                    , status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_category(query_params: dict[str, Any], services_queryset: QuerySet):
    """
    helper function for multiple filters api function
    """
    category_ids = query_params.get("categories", None)
    new_category_ids = catch(category_ids)
    
    services_q_expr = (Q(category__id=int(x)) for x in new_category_ids)
    services_q_expr = reduce(lambda a, b: a | b, services_q_expr)
    
    return services_q_expr, services_queryset

def check_range(query_params: dict[str, Any], services_queryset: QuerySet):
    """
    helper function for multiple filters api function
    """
    min_price, max_price = query_params.get("range")[0][0], query_params.get("range")[1][0]
    min_price, max_price = float(min_price), float(max_price)
    q_expr = Q(price__range=(min_price, max_price))
    
    return q_expr, services_queryset

def search_func(query_params: dict[str, Any], services_queryset: QuerySet):
    words: str = query_params.get("search").split("_")
    q_exprs = (Q(search=SearchQuery(word)) for word in words)
    q_func = reduce(lambda x, y: x | y, q_exprs)
    
    services_queryset = services_queryset.annotate(search=SearchVector("en_title", "ar_title"))
    
    return q_func, services_queryset

def check_rate(query_params: dict[str, Any], services_queryset: QuerySet):
    rates = catch(query_params.get("rates"))
    
    services_queryset = services_queryset.prefetch_related("service_rates")
    services_queryset = services_queryset.annotate(avg_rate=Avg("service_rates__rate"))
    
    q_expr = (Q(avg_rate__gt=rate-0.5) & Q(avg_rate__lte=rate+0.5) for rate in rates)
    q_expr = reduce(lambda x, y: x | y, q_expr)
    
    return q_expr, services_queryset

def check_distance(query_params: dict[str, Any], services_queryset: QuerySet):
    location = Point(query_params.get("distance"), srid=4326)
    
    services_q_expr = Q(provider_location__location__distance_lt=(location, 1000000))
    services_queryset = services_queryset.annotate(
        distance=Distance("provider_location__location", location)).order_by("distance")
    
    return services_q_expr, services_queryset

def get_pagination(pagination_number: int):
    a = pagination_number // 2
    b = pagination_number - a
    return a, b

def get_callables(query_params: dict[str, Any]):
    new_query_params = query_params.copy()
    
    # taking care of pagination number
    pagination_number = new_query_params.pop("pagination_number", None)
    if pagination_number is None:
        pagination_number = 9
    else:
        pagination_number = int(pagination_number[0])
    
    # switching longitude and latitude to distance within query_params
    if new_query_params.get("longitude") and new_query_params.get("latitude"):
        longitude, latitude = new_query_params.pop("longitude")[0], new_query_params.pop("latitude")[0]
        new_query_params["distance"] = float(longitude), float(latitude)
    
    # switching min_price and max_price to price__range within query_params
    if new_query_params.get("min_price") and new_query_params.get("max_price"):
        min_price, max_price = new_query_params.pop("min_price"), new_query_params.pop("max_price")
        new_query_params["range"] = min_price, max_price
    
    callables_hashtable = {
        "distance": check_distance, "search": search_func,
        "rates": check_rate, "range": check_range,
        "categories": check_category
    }
    
    callables = [callables_hashtable[key] for key in new_query_params.keys()]
    return callables, new_query_params, pagination_number


@decorators.api_view(["GET", ])
@decorators.permission_classes([])
def search_in_provider_services(request: HttpRequest, provider_id: int):
    # first we get the language and query_params, then we make main querysets
    language, query_params = request.META.get("Accept-Language"), request.query_params
    services_main_queryset = models.Service.objects
    
    # then we get the callabels which mapped with the served query_params, and take care of pagination num
    callables, query_params, pagination_number = get_callables(query_params)
    
    # then we prepare the Q_exprs that will filter the querysets
    # we stand on callabels and query_params from the last step
    services_Q_exprs = set()
    for func in callables:
        services_Q_expr, services_main_queryset = func(query_params, services_main_queryset)
        services_Q_exprs.add(services_Q_expr)
    
    # here we apply filtering (if exists) on the querysets
    services_main_queryset = services_main_queryset.filter(
        provider_location__service_provider=provider_id ,*services_Q_exprs)
    
    # paginate the queryset under the client-side rules
    services_paginator = custom_pagination_function(pagination_number)
    paginated_services = services_paginator.paginate_queryset(services_main_queryset, request)
    
    # serializing the queryset data
    serialized_services = serializers.RUDServicesSerializer(paginated_services, many=True, language=language)
    
    return Response(data=serialized_services.data, status=status.HTTP_200_OK)
