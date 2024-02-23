from django.db import models

from orders.models import OrderItem



class Delivery(models.Model):
    order = models.OneToOneField(
        OrderItem, on_delete=models.CASCADE, null=False, related_name="delivery", primary_key=True)
    delivered = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.order.product.en_title} -> {'Delivered' if self.delivered else 'Not Delivered'}"
