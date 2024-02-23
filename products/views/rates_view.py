from rest_framework import viewsets, decorators
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework import generics

from django.http import HttpRequest

from typing import Optional

from notification.models import Notification
from products import models, serializers



class CreateRate(generics.CreateAPIView):
    queryset = models.ProductRates.objects
    serializer_class = serializers.RateSerializer
    
    def create(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        data["user"] = request.user.id
        
        serializer = self.get_serializer(data=data, fields={"language": request.META.get("Accept-Language")})
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
        except:
            return Response({
                "message": "this user already rates this product, he can't rate it again"
            }, status=status.HTTP_403_FORBIDDEN)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="User"
            , ar_content="تمت إضافة التقييم"
            , en_content="Rate added")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RatesViewSet(viewsets.ModelViewSet):
    queryset = models.ProductRates.objects
    serializer_class = serializers.RateSerializer
    
    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("fields", {"language": self.request.META.get("Accept-Language")})
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        return Response({"message": "Not allowed method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance], many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=request.user.email, receiver_type="User"
            , ar_content="تم تعديل التقييم"
            , en_content="Rate updated")
        
        return Response(resp.data, status=resp.status_code)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver=self.request.user.email, receiver_type="User"
            , ar_content="تم حذف التقييم"
            , en_content="Rate deleted")
        
        return super().perform_destroy(instance)


@decorators.api_view(["GET", ])
def user_rates(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    
    queryset = models.ProductRates.objects.filter(user=user_id)
    serializer = serializers.RateSerializer(queryset, many=True, fields={"language": language})
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_rates(request: HttpRequest, provider_id: Optional[int]):
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    
    queryset = models.ProductRates.objects.filter(
        product__service_provider_location__service_provider=provider_id)
    serializer = serializers.RateSerializer(queryset, many=True, fields={"language": language})
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def product_rates(request: HttpRequest, product_id: int):
    language = request.META.get("Accept-Language")
    queryset = models.ProductRates.objects.filter(product=product_id)
    serializer = serializers.RateSerializer(queryset, many=True, fields={"language": language})
    
    return Response(serializer.data, status=status.HTTP_200_OK)
