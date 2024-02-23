from rest_framework import serializers

from django.db.models import QuerySet

from .helpers import FileMixin

from . import models


class CreateServicesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Service
        fields = "__all__"
    
    def to_representation(self, instance: models.Service):
        return {
            "id": instance.id
            , "provider_location_id": instance.provider_location.id
            , "provider_name": instance.provider_location.service_provider.business_name
            , "category_title": instance.category.en_name
            , "ar_title": instance.ar_title
            , "en_title": instance.en_title
            , "ar_description": instance.ar_description
            , "en_description": instance.en_description
            , "images": instance.image.split(",")
            , "price": instance.price
            , "discount_ammount": instance.discount_ammount
            , "created_at": instance.created_at
            , "updated_at": instance.updated_at
        }


class RUDServicesSerializer(serializers.ModelSerializer, FileMixin):
    
    class Meta:
        model = models.Service
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = language
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def update(self, instance, validated_data):
        images_paths = instance.image
        self.delete_images(images_paths)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance: models.Service):
        category = instance.category
        rates: QuerySet[models.ServiceRates] = instance.service_rates.all()
        
        return {
            "id": instance.id
            , "provider_location_id": instance.provider_location.id
            , "provider_name": instance.provider_location.service_provider.business_name
            , "category_id": instance.category.id
            , "category_name": category.en_name if self.language == "en" else category.ar_name
            , "title": instance.ar_title if self.language == "ar" else instance.en_title
            , "description": instance.ar_description if self.language == "ar" else instance.en_description
            , "images": instance.image.split(",")
            , "price": instance.price
            , "discount_ammount": instance.discount_ammount
            , "created_at": instance.created_at
            , "updated_at": instance.updated_at
            , "rates" : {
                "avg_rate": instance.average_rating
                , "5 stars": rates.filter(rate=5).count()
                , "4 stars": rates.filter(rate=4).count()
                , "3 stars": rates.filter(rate=3).count()
                , "2 stars": rates.filter(rate=2).count()
                , "1 stars": rates.filter(rate=1).count()
                , "0 stars": rates.filter(rate=0).count()
            }
        }


class ServiceRatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceRates
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = language
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def validate(self, attrs):
        rate = attrs.get("rate")
        if rate is not None and 0 <= rate <= 5:
            return super().validate(attrs)
        
        raise serializers.ValidationError({"error": "service rate must be between 0 and 5"})
    
    def to_representation(self, instance: models.ServiceRates):
        return {
            "rate_id": instance.id
            , "user_id": instance.user.id
            , "user_email": instance.user.email
            , "service_id": instance.service.id
            , "service_tile": instance.service.en_title if self.language == "en" else instance.service.ar_title
            , "rate": instance.rate
        }
