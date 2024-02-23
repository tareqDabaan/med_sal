from rest_framework import serializers

from .models import Appointments, RejectedAppointments



class AppointmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointments
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: Appointments):
        original_repr =  super().to_representation(instance)
        original_repr["user_email"] = instance.user.email
        original_repr["service_title"] = instance.service.ar_title if self.language == "ar" else instance.service.en_title
        original_repr["location_id"] = instance.service.provider_location.id
        original_repr["provider_id"] = instance.service.provider_location.service_provider.id
        original_repr["provider_email"] = instance.service.provider_location.service_provider.email
        original_repr["provider_business_name"] = instance.service.provider_location.service_provider.business_name
        
        return original_repr


class ShowAppointmentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointments
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        language = kwargs.get("language")
        if not language:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: Appointments):
        return {
            "date": instance.date
            , "details": {
                "from_time": instance.from_time
                , "to_time": instance.to_time
                , "patient_id": instance.user.id
                , "patient_email": instance.user.email
                , "service_id": instance.service.id
                , "service_title": instance.service.en_title if self.language == "en" else instance.service.ar_title
                , "provider_id": instance.service.provider_location.service_provider.id
                , "provider_business_name": instance.service.provider_location.service_provider.business_name
                , "location_id": instance.service.provider_location.id
                , "diagonsis": instance.diagonsis
                , "status": instance.status
                , "created_at": instance.created_at
            }
        }


class RejectedSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RejectedAppointments
        fields = "__all__"
    
    def __init__(self, instance=None, data=..., **kwargs):
        langauge = kwargs.get("language")
        if not langauge:
            self.language = None
        else:
            self.language = kwargs.pop("language")
        
        super().__init__(instance, data, **kwargs)
    
    def to_representation(self, instance: RejectedAppointments):
        appointment = instance.appointment
        return {
            "id": instance.id
            , "service_id": appointment.service.id
            , "service_title": appointment.service.en_title if self.language == "en" else appointment.service.ar_title
            , "appointment_id": appointment.id
            , "provider_id": appointment.service.provider_location.service_provider.id
            , "provider_email": appointment.service.provider_location.service_provider.email
            , "locaiton_id": appointment.service.provider_location.id
            , "reason": instance.reason
            , "read": instance.read
            , "created_at": instance.created_at
        }
