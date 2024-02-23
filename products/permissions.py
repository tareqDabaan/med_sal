from rest_framework import permissions

from permissions import helpers
from utils.method_truth import request_method_table


class HasPermissionOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return self.check_permission(request)
        
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return self.check_permission(request=request, model_name=obj.__class__.__name__)
    
    def check_permission(self, request, model_name: str=None):
        
        if not request.user.is_authenticated:
            return False
        
        method_name = request_method_table(request.method)
        codename = f"{method_name}_product"
        if model_name is not None:
            model_name = model_name.lower()
            codename = f"{method_name}_{model_name}"
        
        group = helpers.Groups()
        result = group.has_permission(codename, request.user.groups.first())
        
        return result