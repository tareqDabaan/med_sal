from rest_framework import serializers

from . import models

from service_providers.models import ServiceProviderLocations



class RateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ProductRates
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        fields = kwargs.get("fields")
        if not fields:
            self.language = None
        else:
            fields = kwargs.pop("fields")
            self.language = fields.get("language")
        
        super().__init__(instance, data, **kwargs)
        
    def validate(self, attrs):
        rate = attrs.get("rate")
        if int(rate) > 5 or int(rate) < 0:
            raise ValueError("Product Rate must be under 5 and more than or equal 0")
        
        return super().validate(attrs)
    
    def to_representation(self, instance: models.ProductRates):
        response = super().to_representation(instance)
        product_title = instance.product.ar_title if self.language == "ar" else instance.product.en_title
        
        resp = {
            "rate_id": response.get("id")
            , "actual_rate": response.get("rate")
            , "user_id": response.get("user")
            , "user_email": instance.user.email
            , "product_id": response.get("product")
            , "product_title": product_title
        }
        
        return resp


class ProudctSerializer(serializers.ModelSerializer):
    service_provider_location = ServiceProviderLocations()
    
    class Meta:
        model = models.Product
        fields = ("id", "service_provider_location", "quantity", "ar_title"
                , "en_title", "ar_description", "en_description", "images", "price", )
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: models.Product):
        category = instance.service_provider_location.service_provider.category
        
        return {
            "id": instance.id
            , "service_provider": instance.service_provider_location.service_provider.business_name
            , "service_provider_location": instance.service_provider_location.id
            , "category_id": category.id
            , "category_title": category.ar_name if self.language == "ar" else category.en_name 
            , "quantity": instance.quantity
            , "title": instance.ar_title if self.language == "ar" else instance.en_title
            , "description": instance.ar_description if self.language == "ar" else instance.en_description
            , "images": instance.images.split(",")
            , "price": instance.price
            , "discount_ammount": instance.discount_ammount
            , "rates": {
                "avg_rate": instance.average_rating
                , "5": instance.product_rates.filter(rate=5).count()
                , "4": instance.product_rates.filter(rate=4).count()
                , "3": instance.product_rates.filter(rate=3).count()
                , "2": instance.product_rates.filter(rate=2).count()
                , "1": instance.product_rates.filter(rate=1).count()
                , "0": instance.product_rates.filter(rate=0).count()
            }
        }
