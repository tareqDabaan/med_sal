from rest_framework import viewsets, decorators
from rest_framework.response import Response
from rest_framework import status

from django.http import HttpRequest

from typing import Optional

from notification.models import Notification
from utils.permission import authorization
from orders import models, serializers



class CartView(viewsets.ModelViewSet):
    serializer_class = serializers.CartSerializer
    queryset = models.CartItems.objects
    
    def get_serializer(self, *args, **kwargs):
        language = self.request.META.get("Accept-Language")
        kwargs.setdefault("language", language)
        
        return super().get_serializer(*args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        data = request.data
        data["patient"] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver_type="User", receiver=request.user.id
            , ar_content="تم إضافة منتج جديد إلى قائمتك, بانتظار تأكيدك لعملية الشراء"
            , en_content="a new item added to your cart")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def retrieve(self, request, *args, **kwargs):
        queryset = self.queryset.filter(id=self.kwargs.get("pk"))
        if not queryset.exists():
            return Response({"error":"no item exists with this id"})
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver_type="User", receiver=request.user.id
            , ar_content="تم التعديل على العنصر"
            , en_content="item edited")
        
        return Response(resp.data, status=status.HTTP_202_ACCEPTED)
    
    def destroy(self, request, *args, **kwargs):
        resp = super().destroy(request, *args, **kwargs)
        
        Notification.objects.create(
            sender="System", sender_type="System"
            , receiver_type="User", receiver=request.user.id
            , ar_content="تم حذف العنصر من قائمة الانتظار"
            , en_content="item deleted from cart")
        
        return Response(resp.data, status=resp.status_code)
    
    def list(self, request, *args, **kwargs):
        return Response()

@decorators.api_view(["GET", ])
@authorization("cartitems")
def user_cart(request: HttpRequest, user_id: Optional[int]):
    user_id = user_id or request.user.id
    language = request.META.get("Accept-Language")
    
    queryset = models.CartItems.objects.filter(patient=request.user.id)
    serializer = serializers.CartSerializer(queryset, many=True, language=language)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
