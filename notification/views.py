from rest_framework import generics, decorators
from rest_framework import status, permissions
from rest_framework.response import Response

from django.http import HttpRequest

from . import models, serializers



class RUDNotification(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Notification.objects
    serializer_class = serializers.NotificationSerializer
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs["language"] = language
        
        return super().get_serializer(*args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer([instance, ], many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.IsAdminUser, ])
def all_notification(request: HttpRequest):
    language = request.META.get("Accept-Language")
    queryset = models.Notification.objects.all()
    serializer = serializers.NotificationSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
def your_notifications(request: HttpRequest):
    language = request.META.get("Accept-Language")
    user_type = request.user.user_type
    hash_table = {
        "ADMIN": ("System", "System")
        , "USER": ("User", request.user.email)
        , "SERVICE_PROVIDER": ("Service_Provider", request.user.email)
    }
    
    queryset = models.Notification.objects.filter(
        receiver_type=hash_table[user_type][0], receiver=hash_table[user_type][1])
    serializer = serializers.NotificationSerializer(queryset, many=True, language=language)
    return Response(serializer.data, status=status.HTTP_200_OK)
