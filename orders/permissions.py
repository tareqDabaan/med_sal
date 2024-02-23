from rest_framework import permissions

from typing import Optional

from permissions import helpers
from utils.method_truth import request_method_table


class HasPermission(permissions.BasePermission):
    
    # def __init__(self, model_name: Optional[str]) -> None:
    #     self.model_name = model_name
    #     super().__init__()
    
    def has_permission(self, request, view) -> bool:
        return self.check_permission(request, "cart")
    
    def has_object_permission(self, request, view, obj) -> bool:
        return self.check_permission(request, "cart")
    
    def check_permission(self, request, model_name: None=None) -> bool:
        
        if not request.user.is_authenticated:
            return False
        
        method_name = request_method_table(request.method)
        codename = f"{method_name}_cart"
        if model_name is not None:
            model_name = model_name.lower()
            codename = f"{method_name}_{model_name}"
        
        group = helpers.Groups()
        result = group.has_permission(codename, request.user.groups.first())
        return result


class ListItemsPermission(permissions.BasePermission):
    
    def has_permission(self, request, view) -> bool:
        return self.check_permission(request)
    
    def has_object_permission(self, request, view, obj) -> bool:
        return self.check_permission(request)
    
    def check_permission(self, request) -> bool:
        
        if not request.user.is_authenticated:
            return False
        
        codename = f"list_orderitems"
        
        group = helpers.Groups()
        result = group.has_permission(codename, request.user.groups.first())
        
        return result