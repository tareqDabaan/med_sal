from rest_framework import decorators, status, permissions
from rest_framework.response import Response

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Q

from django.http import HttpRequest

from services import models as smodels, serializers as sserializer
from services import serializers

from functools import reduce


#
@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def services_by_location(request: HttpRequest, location_id: int):
    """
    list location services
    need location_id 
    """
    language = request.META.get("Accept-Language")
    queryset = smodels.Service.objects.filter(provider_location=location_id)
    
    if not queryset.exists():
        return Response({"message": "Database has no location with this location_id"})
    
    serializer = serializers.RUDServicesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def services_by_category(request: HttpRequest, category_id: int):
    """
    list category services
    need category_id
    """
    language = request.META.get("Accept-Language")
    services = smodels.Service.objects.filter(category=category_id)
    
    if not services:
        return Response({"message": "No services found in this category"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = sserializer.RUDServicesSerializer(services, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


# 
@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def services_by_distance(request: HttpRequest, service_name: str, longitude: str, latitude: str):
    """
        An api to list services filtered by distance ordered for nearest to farthest.
        lat and lon are required
        ?latitude=<integer>, longitude=<integer> & service_name=<string>
        
        ### nearest_locations = Location.objects.annotate(
            ### distance=Distance('point', given_point)).order_by('distance')[:3] 
    """
    language = request.META.get("Accept-Language")
    
    location = Point(float(longitude), float(latitude), srid=4326)
    service_name = service_name.split("_")
    Q_expr = (Q(en_title__icontains=x) | Q(ar_title__icontains=x) for x in service_name)
    Q_func = reduce(lambda x,y: x & y, Q_expr)
    
    services = smodels.Service.objects.filter(Q_func,
        provider_location__location__distance_lt=(location, 1000000)
        ).annotate(distance=Distance("provider_location__location", location)).order_by("distance")
    
    if not services.exists():
        return Response(
            {"message": "No service provider in this area"}
            , status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.RUDServicesSerializer(services, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


#
@decorators.api_view(["GET"])
@decorators.permission_classes([permissions.AllowAny, ])
def services_by_name(request:HttpRequest, service_name: str):
    """
        An api to list services filtered by it's name (ar & en)
        services name is required
        ?name=<string>
    """
    language = request.META.get("Accept-Language")
    text_seq = service_name.split("_")
    Q_expr = (Q(en_title__icontains=x) | Q(ar_title__icontains=x) for x in text_seq)
    q_func = reduce(lambda x,y: x & y, Q_expr)
    services = smodels.Service.objects.filter(q_func)
    
    if not services.exists():
        return Response({'error': 'No services found with that name'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = sserializer.RUDServicesSerializer(services, many=True, language=language)
    return Response(serializer.data, status = status.HTTP_200_OK)
