from rest_framework import generics, status, permissions
from rest_framework.response import Response

from django.http import HttpRequest

from . import serializers, models



class CreateContcatUs(generics.CreateAPIView):
    serializer_class = serializers.ContactUsSerializer
    permission_classes = () # means everybody
    queryset = models.ContactUs.objects
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ListContactUs(generics.ListAPIView):
    serializer_class = serializers.ContactUsSerializer
    permission_classes = (permissions.IsAdminUser, )
    queryset = models.ContactUs.objects
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RUDContactUs(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ContactUsSerializer
    permission_classes = (permissions.IsAdminUser, )
    queryset = models.ContactUs.objects
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request: HttpRequest, *args, **kwargs):
        data = request.data
        if data.get("read"):
            data = data.copy()
            data["read_by"] = request.user.id
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
