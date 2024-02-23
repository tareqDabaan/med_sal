from rest_framework import viewsets, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from utils.permission import authorization_with_method
from notification.models import Notification
from services import models, serializers



@decorators.api_view(["DELETE", "PATCH", "PUT"])
def update_delete_rate(request: HttpRequest, rate_id: int):
    language = request.META.get("Accept-Language")
    instance = models.ServiceRates.objects.filter(id=rate_id)
    if not instance.exists():
        return Response({"error": "No rate exists with this id"}, status=status.HTTP_404_NOT_FOUND)
    
    # if he isn't the rate owner, return permission denied
    instance = instance.first()
    if not request.user == instance.user:
        return Response(
            {"error": "You don't have permission to make this action"}
            , status=status.HTTP_403_FORBIDDEN)
    
    def delete_instance(instance: models.ServiceRates):
        instance.delete()
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=instance.user.email, receiver_type="User"
            , ar_content="تم حذف التقييم", en_content="rate deleted")
        
        return Response({"Done": "Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    def update_instance(instance: models.ServiceRates):
        partial = True if request.method == "PATCH" else False
        serializer = serializers.ServiceRatesSerializer(
            instance, data=request.data, partial=partial, language=language)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="User"
            , ar_content="تم تعديل التقييم", en_content="rate updated")
        
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    return delete_instance(instance) if request.method == "DELETE" else update_instance(instance)

#
@decorators.api_view(["GET"])
@decorators.permission_classes([])
def get_rate(request: HttpRequest, rate_id: int):
    language = request.META.get("Accept-Language")
    instance = models.ServiceRates.objects.filter(id=rate_id)
    if not instance.exists():
        return Response({"error": "No rate exists with this id"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ServiceRatesSerializer(instance, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["POST", ])
def create_rate(request: HttpRequest):
    
    def perform_create(serializer):
        serializer.save()
    
    language = request.META.get("Accept-Language")
    request.data["user"] = request.user.id
    
    serializer = serializers.ServiceRatesSerializer(data=request.data, language=language)
    serializer.is_valid(raise_exception=True)
    
    try:
        perform_create(serializer)
    except:
        return Response(
            {"error": "this user already rate this service, user can't rate same service twice"}
            , status=status.HTTP_403_FORBIDDEN)
    
    Notification.objects.create(
        sender="System", sender_type="System"
        , receiver=request.user.email, receiver_type="User"
        , ar_content="تمت إضافة التقييم", en_content="rate added")
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

#
@decorators.api_view(["GET", ])
@authorization_with_method("list", "servicerates")
def all_rates(request: HttpRequest):
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.all()
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
def location_rates(request: HttpRequest, location_id: int):
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.filter(service__provider_location=location_id)
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
def provider_rates(request: HttpRequest, provider_id: int):
    provider_id = provider_id or request.user.id
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.filter(
        service__provider_location__service_provider=provider_id)
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
def user_rates(request: HttpRequest, user_id: int):
    user_id = user_id or request.user.id
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.filter(user__id=user_id)
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

#
@decorators.api_view(["GET", ])
def service_rates(request: HttpRequest, service_id: int):
    """
    return specific service rates with details
    """
    language = request.META.get("Accept-Language")
    queryset = models.ServiceRates.objects.filter(service=service_id)
    if not queryset.exists():
        return Response({"message": "No rates for this service"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ServiceRatesSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
