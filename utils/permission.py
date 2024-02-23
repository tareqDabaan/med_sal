from rest_framework import permissions, exceptions

from django.http import HttpRequest

from typing import Optional

from permissions import helpers
from .method_truth import request_method_table


class HasPermission(permissions.BasePermission):
    
    def __init__(self, model_name: Optional[str]) -> None:
        self.model_name = model_name
        super().__init__()
    
    def has_permission(self, request, view) -> bool:
        return self.check_permission(request)
    
    def has_object_permission(self, request, view, obj) -> bool:
        return self.check_permission(request)
    
    def check_permission(self, request) -> bool:
        
        if not request.user.is_authenticated:
            return False
        
        method_name = request_method_table(request.method)
        codename = f"{method_name}_{self.model_name.lower()}"
        
        group = helpers.Groups()
        result = group.has_permission(codename, request.user.groups.first())
        return result

class HasPermissionAndOwner(permissions.BasePermission):
    
    def __init__(self, model_name: Optional[str]) -> None:
        self.model_name = model_name
        super().__init__()
    
    def has_permission(self, request, view) -> bool:
        return self.check_permission(request)
    
    def has_object_permission(self, request, view, obj) -> bool:
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        return self.check_permission(request) and (request.user == obj.user or request.user.is_staff)
    
    def check_permission(self, request) -> bool:
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        method_name = request_method_table(request.method)
        codename = f"{method_name}_{self.model_name.lower()}"
        
        group = helpers.Groups()
        result = group.has_permission(codename, request.user.groups.first())
        return result


def authorization(model_name: str):
    
    def middle_func(original_func):
        
        def wrapper_func(*args, **kwargs):
            request: HttpRequest = args[0]
            
            if not request.user.is_authenticated:
                return False
            
            method_name = request_method_table(request.method)
            codename = f"{method_name}_{model_name}"
            
            group = helpers.Groups()
            result = group.has_permission(codename, request.user.groups.first())
            if result is True:
                return original_func(*args, **kwargs)
            
            raise exceptions.PermissionDenied("you don't have permission to access this")
        
        return wrapper_func
    
    return middle_func


def authorization_with_method(method_name: str, model_name: str):
    
    def middle_func(original_func):
        
        def wrapper_func(*args, **kwargs):
            request: HttpRequest = args[0]
            
            if not request.user.is_authenticated:
                return False
            
            codename = f"{method_name}_{model_name}"
            
            group = helpers.Groups()
            result = group.has_permission(codename, request.user.groups.first())
            if result is True:
                return original_func(*args, **kwargs)
            
            raise exceptions.PermissionDenied("you don't have permission to access this")
        
        return wrapper_func
    
    return middle_func
