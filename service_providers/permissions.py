from rest_framework import permissions

from django.http import HttpRequest

from permissions.helpers import Groups
from utils.method_truth import request_method_table


"""
- Admins Permissions (staff user):
    - Modify any service_provider data 
    - Have access to all service_providers data
    - Can retrieve a specific service_provider data using his (ID)
    - Change account status for a service_provider 

- Authenticated users permissions:
    - Retrieve a specific service_provider data using his (ID)
    - An authenticated user logged in as a service_provider can update his own data 

- Not Authenticated users permissions:
    - Can login as a service_provider (Create a new service_provider)
"""

class UnAuthenticated(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, view):
        return not request.user.is_authenticated


class LocationsPermissions(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_anonymous:
            return False
        
        codename = f"{request_method_table(request.method)}_serviceproviderlocations"
        group = Groups()
        result = group.has_permission(codename, request.user.groups.first())
        
        return result
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.service_provider.email == request.user.email or request.user.is_staff



class UpdateRequestsPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            codename = f"{request_method_table(request.method)}_updateprofilerequests"
            group = Groups()
            result = group.has_permission(codename, request.user.groups.first())
            
            return result
        
        return False
