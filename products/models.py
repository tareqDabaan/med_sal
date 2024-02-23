from django.db.models import Avg
from django.conf import settings
from django.db import models

from service_providers.models import ServiceProviderLocations



class Product(models.Model):
    service_provider_location = models.ForeignKey(
        ServiceProviderLocations, on_delete=models.CASCADE, null=False)
    quantity = models.PositiveIntegerField(default=0)
    ar_title = models.CharField(max_length=128, null=False)
    en_title = models.CharField(max_length=128, null=False)
    ar_description = models.TextField(null=False)
    en_description = models.TextField(null=False)
    images = models.CharField(max_length=255)
    price = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    discount_ammount = models.PositiveSmallIntegerField(default=0, null=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self) -> str:
        category = self.service_provider_location.service_provider.category
        return f"prt_id: {self.id}, prt_en_title: {self.en_title}, prt_category: {category}"
    
    @property
    def average_rating(self):
        return self.product_rates.all().aggregate(Avg("rate", default=0))["rate__avg"]
    
    class Meta:
        ordering = ["id", ]


class ProductRates(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_rates")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_rates")
    rate = models.SmallIntegerField(default=0)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ["user", "product", ],
                name="user_product_constraint",
            ),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} -> {self.product.en_title}"
