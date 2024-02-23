from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import ServiceProvider, ServiceProviderLocations, UpdateProfileRequests
from users.models import Admins

Users = get_user_model()



class ServiceProviderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceProvider
        fields = (
            'id', 'user', "category", "bank_name", "business_name"
            , "iban", "swift_code", "provider_file", "account_status"
            , )
        
    def validate(self, attrs):
        return super().validate(attrs)


class ServiceProviderUpdateRequestSerializer(serializers.ModelSerializer):
    sent_data = serializers.JSONField(required=True)
    
    class Meta:
        model = UpdateProfileRequests
        fields = '__all__'
        read_only_fields = ['user_requested']
    
    def to_representation(self, instance):
        origin_repr = super().to_representation(instance)
        
        admin_name = Admins.objects.filter(id=origin_repr["checked_by"])
        if admin_name.exists():
            admin_name = admin_name.first().email
        else: 
            admin_name = None
        
        origin_repr["checked_by_email"] = admin_name
        return origin_repr


class LocationSerializerSafe(serializers.ModelSerializer):
    service_provider = serializers.StringRelatedField()
    
    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceProviderLocations
        fields = '__all__'
