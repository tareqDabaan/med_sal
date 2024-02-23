from django.urls import path

from . import views


app_name = "contact_us"

urlpatterns = [
    # create for everybody
    path("create/", views.CreateContcatUs.as_view(), name="create_contact_us"),
    
    # list for admins and super admins (is_staff == True)
    path("list/", views.ListContactUs.as_view(), name="list_contact_us"),
    
    # retrieve, update, delete for admins and super admins (is_staff == True)
    path("<int:pk>/", views.RUDContactUs.as_view(), name="rud_contact_us"),
]
