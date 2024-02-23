from rest_framework import serializers

from django.db import connection

from .models import Category


class CategoryCUDSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get('language')
        if language:
            self.language = kwargs.pop("language")
        else:
            self.language = None
        super().__init__(instance, data, **kwargs)
    
    def create(self, validated_data):
        query = f"insert into category_category (en_name, ar_name) \
            values ('{validated_data['en_name']}', '{validated_data['ar_name']}')"
        
        if validated_data.get("parent"):
            query = f"insert into category_category (en_name, ar_name, parent_id) \
                values ('{validated_data['en_name']}', '{validated_data['ar_name']}' \
                , '{validated_data['parent'].id}')"
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            
        return Category.objects.all().last()


class CategorySerializer(CategoryCUDSerializer):
    
    def to_representation(self, instance):
        origin_repr = super().to_representation(instance)
        
        opposite_language = "en" if self.language == "ar" else "ar"
        origin_repr.pop(f"{opposite_language}_name")
        origin_repr["name"] = origin_repr.pop(f"{self.language}_name")
        
        return origin_repr