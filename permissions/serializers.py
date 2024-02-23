from rest_framework import serializers

from django.contrib.auth import models
from django.contrib.contenttypes.models import ContentType


class PermissionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Permission
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Group
        fields = "__all__"


class ContentTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ContentType
        fields = "__all__"
