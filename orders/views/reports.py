from rest_framework.response import Response
from rest_framework import decorators
from rest_framework import status

from django.http import HttpRequest
from django.db.models import F

from typing import Optional

from orders import models, serializers

from utils.permission import authorization_with_method



@decorators.api_view(["GET", ])
@authorization_with_method("list", "orderitems")
def provider_report(request: HttpRequest):
    language = request.META.get("Accept-Language")
    
    query_params = request.query_params.copy()
    try:
        provider_id = int(query_params.pop("provider_id")[0])
    except:
        provider_id = request.user.id
    
    def validate_params(query_params):
        params = ["day", "month", "year"]
        return {param: query_params[param] for param in query_params if param in params}
    
    query_params = validate_params(query_params)
    additional_fields = {f"last_update__{param}": value for param, value in query_params.items()}
    queryset = models.OrderItem.objects.filter(
        product__service_provider_location__service_provider=provider_id
        , status="ACCEPTED", **additional_fields).annotate(total_price= F("price") * F("quantity"))
    
    serializer = serializers.ReportItemSerialzier(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@authorization_with_method("list", "orderitems")
def location_report(request: HttpRequest, location_id: int):
    language = request.META.get("Accept-Language")
    
    def validate_params(query_params):
        params = ["day", "month", "year"]
        return {param: query_params[param] for param in query_params if param in params}
    
    query_params = validate_params(request.query_params)
    additional_fields = {f"last_update__{param}": value for param, value in query_params.items()}
    queryset = models.OrderItem.objects.filter(
        product__service_provider_location=location_id, status="ACCEPTED"
        , **additional_fields).annotate(total_price= F("price") * F("quantity"))
    
    serializer = serializers.ReportItemSerialzier(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def user_report(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.OrderItem.objects.filter(
        order__patient=user_id).annotate(total_price= F("price") * F("quantity"))
    serializer = serializers.ReportItemSerialzier(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
