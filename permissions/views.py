from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework import decorators

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from . import serializers, helpers


Users = get_user_model()


class ContentTypeView(viewsets.ModelViewSet):
    queryset = ContentType.objects
    serializer_class = serializers.ContentTypeSerializer
    permission_classes = (IsAdminUser, )


class GroupView(viewsets.ModelViewSet):
    queryset = Group.objects
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.GroupSerializer


class PermissionView(viewsets.ModelViewSet):
    queryset = Permission.objects
    permission_classes = (IsAdminUser, )
    serializer_class = serializers.PermissionSerializer


@decorators.api_view(["GET", ])
@decorators.permission_classes([IsAdminUser, ])
def group_permissions(request, pk: int):
    group = helpers.Groups()
    queryset = group.get_permissions(group_id=pk)
    
    serializer = serializers.GroupSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["GET", ])
@decorators.permission_classes([IsAdminUser, ])
def get_user_group(request: HttpRequest, pk):
    group = helpers.Groups()
    query_set = group.get_user_groups(pk)
    
    serializer = serializers.GroupSerializer(query_set, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@decorators.api_view(["DELETE", ])
@decorators.permission_classes([IsAdminUser, ])
def execlude_user_from_group(request: HttpRequest):
    user_id, group_id = int(request.data.get("user_id")), int(request.data.get("group_id"))
    
    group = helpers.Groups()
    group.delete_user_from_group(user_id=user_id, group_id=group_id)
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@decorators.api_view(["POST", ])
@decorators.permission_classes([IsAdminUser, ])
def assign_user_to_group(request: HttpRequest):
    user_id, group_id = int(request.data.get("user_id")), int(request.data.get("group_id"))
    
    group = helpers.Groups()
    result = group.add_user(user_id=user_id, group_id=group_id)
    
    return Response({
        "message": result
    }, status= status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
def assign_permission_to_group(request: HttpRequest):
    permission_id, group_id = int(request.data.get("permission_id")), int(request.data.get("group_id"))
    
    group = helpers.Groups()
    result = group.add_permission(perm_id=permission_id, group_id=group_id)
    
    return Response({
        "message": result
    }, status=status.HTTP_201_CREATED)


@decorators.api_view(["POST", ])
def assign_permissions_to_group(request: HttpRequest):
    perms_ids, group_id = request.data.get("permissions_ids"), int(request.data.get("group_id"))
    
    group = helpers.Groups()
    result = group.add_permissions(group_id=group_id, perms_ids=list(perms_ids))
    
    return Response({
        "message": result
    }, status=status.HTTP_201_CREATED)