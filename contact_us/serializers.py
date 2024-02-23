from rest_framework import serializers

from . import models


class ContactUsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.ContactUs
        fields = "__all__"
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    def create(self, validated_data):
        return super().create(validated_data)
    
    def to_representation(self, instance):
        return super().to_representation(instance)
