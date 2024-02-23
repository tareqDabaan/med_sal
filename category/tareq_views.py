from rest_framework import permissions, decorators, status
from rest_framework.response import Response

from django.db.models import Q

from service_providers.serializers import ServiceProviderSerializer
from service_providers.models import ServiceProvider



@decorators.api_view(["GET", ])
@decorators.permission_classes([permissions.AllowAny, ])
def doctor_category_filter(request):    
    """
        An api that lists the doctors catagory and subcategories (All categories specified under the Doctor)
    """
    try:
        doctors = ServiceProvider.objects.filter(Q(service_provider__category__parent_id = 1)|Q(service_provider__category_id = 1))
    
    except ServiceProvider.DoesNotExist:
        return Response({"Error, service provider doesn't exists"})
    
    serializer = ServiceProviderSerializer(doctors, many = True)
    
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )