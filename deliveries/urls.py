from rest_framework import routers

from django.urls import path, re_path

from deliveries.views import maamoun_views, tareq_views

app_name = "delivery"

router = routers.SimpleRouter()
router.register("", maamoun_views.DeliveryViewSet, basename="delivery_crud")

urlpatterns = [
    # provider deliveries
    re_path(r"provider/(\d{1,})?", maamoun_views.provider_deliveries, name="provider_deliveries"),
    
    # user deliveries
    re_path(r"user/(\d{1,})?", maamoun_views.user_deliveries, name="user_deliveries"),
]

urlpatterns += router.urls
