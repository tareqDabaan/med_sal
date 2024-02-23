from django.contrib.auth.models import Permission, Group
from django.contrib.auth import get_user_model
from django.contrib import admin


from . import models


Users = get_user_model()


# # Register your models here.
# admin.site.unregister(Group)
admin.site.register(Permission)
# admin.site.register(Group)
admin.site.register(models.Users)
# admin.site.register(models.SuperAdmins)