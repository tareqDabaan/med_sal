from rest_framework import serializers

from . import models



class NotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Notification
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance):
        return {
            "id": instance.id
            , "sender": instance.sender
            , "sender_type": instance.sender_type
            , "receiver": instance.receiver
            , "reveiver_type": instance.receiver_type
            , "read": instance.read
            , "content": instance.ar_content if self.language == "ar" else instance.en_content
        }
