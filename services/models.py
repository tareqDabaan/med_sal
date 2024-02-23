from django.db.models import Avg
from django.conf import settings
from django.db import models

from service_providers.models import ServiceProviderLocations
from category.models import Category



class Service(models.Model):
    provider_location = models.ForeignKey(
        ServiceProviderLocations, on_delete=models.CASCADE, related_name="services", null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services", null=False)
    ar_title = models.CharField(max_length=127, null=False)
    en_title = models.CharField(max_length=127, null=False)
    ar_description = models.TextField(null=False)
    en_description = models.TextField(null=False)
    image = models.CharField(max_length=256, null=False)
    price = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    discount_ammount = models.PositiveSmallIntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.en_title}, category: {self.category.en_name}, provider: {self.provider_location.service_provider.business_name}"
    
    @property
    def average_rating(self):
        return self.service_rates.all().aggregate(Avg("rate", default=0))["rate__avg"]
    
    class Meta:
        ordering = ["id", ]

class ServiceRates(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_services_rates")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_rates")
    rate = models.SmallIntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["user", "service", ],
                name="user_service_constraint",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} -> {self.service.en_title}"
