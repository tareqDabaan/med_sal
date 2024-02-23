from django.urls import path, re_path
from rest_framework import routers

from orders.views import ( 
    cart_views, tareq_views, orders_views, rejected_orders_views, order_items_views, reports
    )


app_name = "orders"

router = routers.SimpleRouter()

router.register("cart", cart_views.CartView, basename="cart")
router.register("rejected", rejected_orders_views.RejectedOrdersViewSet, basename="rejected_orders")



urlpatterns = [
    # cart
    re_path(r"^cart/user/(\d{1,})?$", cart_views.user_cart, name="user_cart"),
    
    # order
    path("<int:pk>/", orders_views.RetrieveDestroyOrders.as_view(), name="specific_order"),
    path("all/", orders_views.list_all_orders, name="list_all_orders"),
    path("", orders_views.CreateOrder.as_view(), name="create_orders"),
    re_path(r"^user/(\d{1,})?$", orders_views.user_orders, name="user_orders"),
    
    # item
    path("items/<int:pk>/", order_items_views.RetrieveDestroyUpdateItem.as_view(), name="items_rud"),
    path("items/", order_items_views.list_all_items, name="all_items"),
    re_path(r"^items/user/(\d{1,})?$", order_items_views.user_items, name="user_items"),
    
    path("provider/items/", order_items_views.provider_items, name="provider_items"),
    path("provider/stats/", order_items_views.provider_orders_dashboard, name="provider_orders_dashboard"),
    
    # rejected orders
    path("rejected/location/", rejected_orders_views.location_rejected_orders, name="location_rejected_orders"),
    re_path(r"^rejected/user/(\d{1,})?$", rejected_orders_views.user_rejected_orders, name="user_rejected_orders"),
    re_path(r"^rejected/provider/(\d{1,})?$", rejected_orders_views.provider_rejected_orders, name="provider_rejected_orders"),
    
    # items reporst
    path("provider/reports/items/", reports.provider_report, name="provider_report"),
    path("location/reports/items/<int:location_id>/", reports.location_report, name="location_report"),
    re_path(r"^user/reports/items/(\d{1,})?$", reports.user_report, name="user_report"),

]

urlpatterns += router.urls
