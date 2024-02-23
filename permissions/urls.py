from django.urls import path

from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register("groups", views.GroupView, basename="group_view")
router.register("content_type", views.ContentTypeView, basename="content_type")
router.register("permissions", views.PermissionView, basename="permission_view")

app_name = "permissions"

urlpatterns = [
    path("groups/join_user/", views.assign_user_to_group, name="assign_user_to_group"),
    path("groups/execlude_user/", views.execlude_user_from_group, name="execlude_user_from_group"),
    path("group/user/<int:pk>/", views.get_user_group, name="user_group"),
    
    path("groups_permissons/<int:pk>/", views.group_permissions, name="group_permissions"),
    path("groups/add_permission/", views.assign_permission_to_group, name="assign_permission_to_group"),
    path("groups/add_permissions/", views.assign_permissions_to_group, name="assign_permissions_to_group"),    
]

urlpatterns += router.urls
