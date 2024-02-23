from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework import decorators

from django.http import HttpRequest

from .models import UpdateProfileRequests
from . import permissions, serializers

from notification.models import Notification



@decorators.api_view(["GET", ])
def check_provider_update_status(request: HttpRequest):
    provider_id: int = request.user.id
    queryset = UpdateProfileRequests.objects.filter(provider_requested=provider_id)
    if not queryset.exists():
        return Response({
            "message": "there is no such record for this provider"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.ServiceProviderUpdateRequestSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceProviderUpdateRequestViewSet(viewsets.ModelViewSet):
    queryset = UpdateProfileRequests.objects
    serializer_class = serializers.ServiceProviderUpdateRequestSerializer
    permission_classes = (permissions.UpdateRequestsPermission, )
    
    def create(self, request: HttpRequest, *args, **kwargs):
        service_provider, data = request.user.service_provider.id, request.data.copy()
        data["provider_requested"] = service_provider
        
        first_notf = {
            "sender": "System", "sender_type": "System"
            , "receiver": request.user.email, "receiver_type":"Service_Provider"
            , "ar_content": "تعديل الملف الشخصي بانتظار المراجعة"
            , "en_content": "Profile information editing is under revision"}
        
        second_notf = {
            "sender": "System", "sender_type": "System"
            , "receiver": "System", "receiver_type":"System"
            , "ar_content": "تعديل لملف شخصي بانتظار المراجعة"
            , "en_content": "Profile information editing is need revision"}
        
        Notification.objects.bulk_create([Notification(**first_notf), Notification(**second_notf)])
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        request.data["checked_by"] = request.user.id
        return super().update(request, *args, **kwargs)
