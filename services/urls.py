from django.urls import re_path, path

from services.views import maamoun_views, tareq_views, rates_views



app_name = "services"

urlpatterns = [
    
    ### Services ###
    # 1] create service
    path("", maamoun_views.CreateService.as_view(), name="create_service"),
    # 2] all services
    path("all/", maamoun_views.ListAllServices.as_view(), name="all_services"),
    # 3] rud services
    path("<int:pk>/", maamoun_views.ServiceRUD.as_view(), name="service_rud"),
    
    
    ### Services Filters ###
    # multiple filters
    path("search/<int:provider_id>/", maamoun_views.search_in_provider_services, name="search_in_provider_services"),
    # search in services by service name
    path("by_name/<str:service_name>/", tareq_views.services_by_name, name="services_by_name"),
    # list services by distance
    path("distance/<str:service_name>/<str:longitude>/<str:latitude>/", tareq_views.services_by_distance, name="service_by_distance"),
    
    
    ## Category Filters ##
    # category services by name
    path("category/<str:category_name>/", maamoun_views.category_services_by_name, name="category_services_by_name"),
    # list services in a category (by category_id)
    path("category/<int:category_id>/", tareq_views.services_by_category, name="services_for_category"),
    
    
    ## Provider and Location Filters ##
    # provider services #
    re_path(r"^provider/(?P<provider_id>\d+)?$", maamoun_views.provider_services, name="provider_services"),
    # number of services for each category available in specific provider
    path("provider/categories/<int:provider_id>/", maamoun_views.provider_services_by_category, name="provider_services_by_category"),
    # list services by provider location
    path("provider/location/<int:location_id>/", tareq_views.services_by_location, name="service_by_location"),
    # provider services in specific category #
    path("provider/<int:provider_id>/<int:category_id>/", maamoun_views.provider_category_services, name="provider_category_services"),
    
    
    ### Rates ###
    # all rates for admins #
    path("rates/all/", rates_views.all_rates, name="all_rates"),
    # create rates for authenticated users #
    path("rates/create/", rates_views.create_rate, name="create_rate"),
    # get specific rate #
    path("rates/<int:rate_id>/", rates_views.get_rate, name="get_rate"),
    # delete and update rates for rate owner #
    path("rates/delete_or_update/<int:rate_id>/", rates_views.update_delete_rate, name="update_delete_rate"),
    # user rates #
    path("rates/user/<int:user_id>/", rates_views.user_rates, name="user_rates"),
    # provider rates #
    path("rates/provider/<int:provider_id>/", rates_views.provider_rates, name="provider_rates"),
    # location rates #
    path("rates/location/<int:location_id>/", rates_views.location_rates, name="location_rates"),
    # service rates #
    path("<int:service_id>/rates/", rates_views.service_rates, name="service_rates"),
]