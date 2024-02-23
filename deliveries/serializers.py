from rest_framework import serializers

from deliveries import models



class DeliverySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Delivery
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        fields = kwargs.get("fields")
        if not fields:
            self.language = None
        else:
            fields = kwargs.pop("fields")
            self.language = fields.get("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: models.Delivery):
        product = instance.order.product
        
        return {
            "order_id": instance.order.id
            , "product_id": instance.order.product.id
            , "product_title": product.en_title if self.language == "en" else product.ar_title 
            , "delivered": instance.delivered
        }