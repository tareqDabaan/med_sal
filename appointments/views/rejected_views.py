from rest_framework import status, decorators
from rest_framework.response import Response
from rest_framework import generics

from django.http import HttpRequest

from typing import Optional

from appointments import models, serializers

from utils.permission import authorization_with_method
from notification.models import Notification



class CreateRejectedAppointment(generics.CreateAPIView):
    queryset = models.RejectedAppointments.objects
    serializer_class = serializers.RejectedSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver="System", receiver_type="System"
            , en_content="A new rejected order added"
            , ar_content="تم رفض موعد من قبل أحد مزودي الخدمات")
        
        return Response(resp.data, status=status.HTTP_201_CREATED)


class RUDRejectedAppointments(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.RejectedAppointments.objects
    serializer_class = serializers.RejectedSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        return super().get_serializer(*args, **kwargs)
    
    def retrieve(self, request: HttpRequest, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance,], many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@decorators.api_view(["GET", ])
@authorization_with_method("list", "rejectedappointments")
def all_rejected_appointments(request: HttpRequest):
    language = request.META.get("Accept-Language")
    queryset = models.RejectedAppointments.objects.all()
    serializer = serializers.RejectedSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET",])
def user_rejected_appointments(request: HttpRequest, user_id: Optional[int]):
    language = request.META.get("Accept-Language")
    user_id = user_id or request.user.id
    queryset = models.RejectedAppointments.objects.filter(appointment__user=user_id)
    serializer = serializers.RejectedSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def provider_rejected_appointments(request: HttpRequest, provider_id: Optional[int]):
    language = request.META.get("Accept-Language")
    provider_id = provider_id or request.user.id
    queryset = models.RejectedAppointments.objects.filter(
        appointment__service__provider_location__service_provider=provider_id)
    serializer = serializers.RejectedSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def location_rejected_appointments(request: HttpRequest, location_id: int):
    language = request.META.get("Accept-Language")
    location_id = location_id or request.user.id
    queryset = models.RejectedAppointments.objects.filter(
        appointment__service__provider_location=location_id)
    serializer = serializers.RejectedSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)
