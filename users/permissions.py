from rest_framework import permissions

from django.http import HttpRequest

from permissions import helpers
from utils.method_truth import request_method_table



class HavePermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return super().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        
        action_name: str = request_method_table(request.method)
        model_name: str = obj.__class__.__name__
        codename = f"{action_name}_{model_name.lower()}"
        
        group = helpers.Groups()
        result = group.has_permission(codename, request.user.groups.first())
        
        return result


class ListServiceProvider(permissions.BasePermission):
    
    def has_permission(self, request: HttpRequest, view):
        code_name = f"list_service_providers"
        
        group = helpers.Groups()
        result = group.has_permission(code_name, request.user.groups.first())
        
        return result


class IsAdminOrOwner(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request: HttpRequest, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        action_name: str = request_method_table(request.method)
        model_name: str = obj.__class__.__name__
        codename = f"{action_name}_{model_name.lower()}"
        
        group = helpers.Groups()
        result = group.has_permission(codename, request.user.groups.first())
        
        return (request.user.is_staff or obj.id == request.user.id) and result


class HasListUsers(permissions.BasePermission):
    
    def has_permission(self, request: HttpRequest, view):
        group = helpers.Groups()
        result = group.has_permission("list_users", request.user.groups.first())
        
        return result


class UnAuthenticated(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, view):
        return not request.user.is_authenticated
