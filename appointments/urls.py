from django.urls import re_path, path

from appointments.views import appointments_views, rejected_views

app_name = "appointments"



urlpatterns = [
    # appointments
    path("create/", appointments_views.CreateAppointment.as_view(), name="create_appointment"),
    path("<int:pk>/", appointments_views.AppointmentRUD.as_view(), name="rud-appointment"),
    path("provider/dashboard/",
        appointments_views.provider_appointments_dashborad, name="provider_appointments_dashborad"),
    
    re_path(r"^provider/(\d{1,})?$"
            , appointments_views.all_provider_appointments, name="all_provider_appointments"),
    
    path("location/<int:location_id>/"
        , appointments_views.all_location_appointments, name="location_appointments"),
    
    re_path(r"^user/(\d{1,})?$"
            , appointments_views.all_user_appointments, name="all_user_appointments"),
    
    # rejected
    path("rejected/", rejected_views.all_rejected_appointments, name="all_rejected_appointments"),
    
    path("rejected/<int:pk>/"
        , rejected_views.RUDRejectedAppointments.as_view(), name="rud_rejected_appointments"),
    
    path("rejected/create/"
        , rejected_views.CreateRejectedAppointment.as_view(), name="create_rejected_appointment"),
    
    re_path(r"^rejected/user/(\d{1,})?$"
        , rejected_views.user_rejected_appointments, name="user_rejected_appointments"),
    
    re_path(r"^rejected/provider/(\d{1,})?$"
        , rejected_views.provider_rejected_appointments, name="provider_rejected_appointments"),
    
    path("rejected/location/<int:location_id>/"
        , rejected_views.location_rejected_appointments, name="location_rejected_appointments")
]
