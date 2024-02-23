from rest_framework import decorators, status, permissions
from rest_framework.response import Response

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.http import HttpRequest
from django.db.models import Q

from products import models as pmodels, serializers as pserializer



@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def products_by_distance(request: HttpRequest):
    """
        An api to list products filtered by distance ordered for nearest to farthest.
        lat and lon are required
        ?latitude=<integer> & longitude=<integer> 
    """
    language = request.META.get("Accept-Language")
    latitude, longitude = request.query_params.get('latitude'), request.query_params.get('longitude')
    product_name = request.query_params.get("name")
    
    if not (latitude and longitude and product_name):
        return Response(
            {'error': 'Latitude and longitude parameters are required'}
            , status=status.HTTP_400_BAD_REQUEST)
    
    location = Point(float(longitude), float(latitude), srid=4326)
    Q_expression = Q(en_title__icontains=product_name) if language=="en" else Q(ar_title__icontains=product_name)
    
    products = pmodels.Product.objects.filter(en_title__icontains=Q_expression,
        service_provider_location__location__distance_lt=(location, 1000000)
        ).annotate(distance=Distance('service_provider_location__location', location)).order_by('distance')
    
    if not products.exists():
        return Response(
            {"message": "No service provider in this area"}
            , status = status.HTTP_404_NOT_FOUND)
    
    serializer = pserializer.ProudctSerializer(products, many=True, fields={'language':language})
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET"])
@decorators.permission_classes([permissions.AllowAny, ])
def product_filter_by_name(request:HttpRequest):
    """
    An api to list products filtered by it's name (ar & en)
    product name is required
    ?name=<string>
    """
    language = request.META.get("Accept-Language")
    product_name = request.query_params.get('name')
    
    if not product_name:
        return Response({'error': 'Product name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    Q_expression = Q(en_title__icontains=product_name) if language == "en" else Q(ar_title__icontains=product_name)
    products = pmodels.Product.objects.filter(Q_expression)
    
    if not products.exists():
        return Response({'message': 'No products found with that name'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = pserializer.ProudctSerializer(products, many = True, fields = {'language':language})
    return Response(serializer.data, status = status.HTTP_200_OK)
