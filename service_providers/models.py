from django.contrib.gis.db import models

from users.models import Users, Admins
from category.models import Category



class ServiceProvider(Users):
    
    class AccountStatus(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
    
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='service_provider', null=False)
    approved_by = models.ForeignKey(Admins,
                on_delete=models.PROTECT, null=True, related_name='accepted_services')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services_providers")
    business_name = models.CharField(max_length=128, null=False, unique=True)
    bank_name = models.CharField(max_length=128, null=False)
    iban = models.CharField(max_length=40, null=False, unique=True)
    swift_code = models.CharField(max_length=16, null=False, unique=True)
    provider_file = models.FileField(null=True) # null to be False
    account_status = models.CharField(max_length=16,
            choices=AccountStatus.choices, default=AccountStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ServiceProvider"
        verbose_name_plural = "ServiceProviders"
    
    def __str__(self):
        return self.business_name


class ServiceProviderLocations(models.Model):
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="locations")
    location = models.PointField(srid=4326, null=True) # null must be False
    opening = models.TimeField(null=False)
    closing = models.TimeField(null=False)
    crew = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        verbose_name = "ServiceProviderLocations"
        verbose_name_plural = "ServiceProviderLocations"
    
    def __str__(self):
        return self.service_provider.business_name

class UpdateProfileRequests(models.Model):
    class RecordStatus(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
    
    provider_requested = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    checked_by = models.ForeignKey(Admins, null=True, on_delete = models.CASCADE, related_name='admin_approved_profile_requests')
    sent_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    request_status = models.CharField(
        max_length=15, null=False, choices=RecordStatus.choices, default=RecordStatus.PENDING)
    
    def __str__(self):
        return f"UpdateRequest for {self.provider_requested.business_name}"
