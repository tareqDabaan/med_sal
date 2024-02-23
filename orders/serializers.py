from rest_framework import serializers

from django.db import models

from typing import Any

from . import models

from deliveries.models import Delivery


""" **{ the below serializer used in orders_view views }** """ #
class ItemsSerializer(serializers.ModelSerializer):
    """
    to use in orders serializer only
    """
    class Meta:
        fields = ("id", "price", "quantity", "product", "last_update")
        model = models.OrderItem
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if language:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance):
        
        return {
            "order_id": instance.order.id
            , "item_id": instance.id
            , "product_id": instance.product.id
            , "product_name": instance.product.en_title if self.language == "en" else instance.product.ar_title
            , "quantity": instance.quantity
            , "price": instance.price
            , "status": instance.status
            , "last_update": instance.last_update
        }


class OrdersSerializer(serializers.ModelSerializer): #
    items = ItemsSerializer(many=True)
    
    class Meta:
        model = models.Orders
        fields = ("patient", "items",)
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if language:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def create(self, validated_data: dict[str, Any]):
        """
        first we create Order instance without price
        then we make a list of order items
        we use bulk create to create (one or more) OrderItmes objects related with the previous order instance
        then we change the Order instance price with the sum of all OrderItems objects prices
        and we return the Order instance
        """
        patient_obj = validated_data.pop("patient")
        order = models.Orders.objects.create(patient=patient_obj)
        
        OrdersItems = []
        for OrderDict in validated_data.get("items"):
            product, quantity = OrderDict["product"], OrderDict["quantity"] or 1
            price = round(product.price * quantity, 2)
            
            product.quantity -= quantity
            product.save()
            
            item = models.OrderItem(order=order, product=product, quantity=quantity, price=price)
            OrdersItems.append(item)
        
        models.OrderItem.objects.bulk_create(OrdersItems)
        
        return order
    
    def to_representation(self, instance: models.Orders):
        items_queryset = instance.items.all()
        items_serializer = ItemsSerializer(items_queryset, many=True, language=self.language)
        
        return {
            'order_id': instance.id,
            'patient_id': instance.patient.id,
            'created_at': instance.created_at,
            'order_items': items_serializer.data
        }


""" **{ serializer below user in cart views classes and functions}** """ #
class CartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.CartItems
        fields = ("id", "product", "quantity", "patient", )
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if language:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def validate(self, attrs):
        quantity = attrs.get("quantity")
        if quantity <= 0:
            raise serializers.ValidationError({"error": "quantity must be more than 1 or more"})
        
        return super().validate(attrs)
    
    def to_representation(self, instance):
        return {
            "cart_id": instance.id
            , "patient_id": instance.patient.id
            , "product_id": instance.product.id
            , "product_name": instance.product.ar_title if self.language == "ar" else instance.product.en_title
            , "quantity": instance.quantity
            }


class SpecificItemSerialzier(serializers.ModelSerializer):
    
    class Meta:
        model = models.OrderItem
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if language:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def update(self, instance, validated_data: dict[str, Any]):
        status = validated_data.get("status")
        if status == "ACCEPTED":
            try:
                Delivery.objects.create(order=instance)
            except:
                raise serializers.ValidationError({"error": "this item already set to be delivered"})
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance: models.OrderItem):
        return {
            "id": instance.id
            , "order_id": instance.order.id
            , "user_id": instance.order.patient.id
            , "user_email": instance.order.patient.email
            , "location_point": str(instance.product.service_provider_location.location)
            , "product_id": instance.product.id
            , "product_title": instance.product.en_title if self.language == "en" else instance.product.ar_title
            , "quantity": instance.quantity
            , "unit_price": instance.price
            , "status": instance.status
            , "last_update": instance.last_update
        }


class ReportItemSerialzier(serializers.ModelSerializer):
    
    class Meta:
        model = models.OrderItem
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if language:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance):
        return {
            "id": instance.id
            , "order_id": instance.order.id
            , "user_id": instance.order.patient.id
            , "user_email": instance.order.patient.email
            , "product_id": instance.product.id
            , "product_title": instance.product.en_title if self.language == "en" else instance.product.ar_title
            , "quantity": instance.quantity
            , "unit_price": instance.price
            , "total_price": instance.total_price
            , "status": instance.status
            , "last_update": instance.last_update
        }


class RejectedOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.RejectedOrders
        fields = "__all__"
        
    def to_representation(self, instance: models.RejectedOrders):
        original_resp = super().to_representation(instance)
        
        return {
            "order_id": original_resp.get("order")
            , "user_email": instance.order.order.patient.email
            , "reason": original_resp["reason"]
            , "read": instance.read
            }
