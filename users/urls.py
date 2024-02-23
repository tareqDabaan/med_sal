from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "users"

urlpatterns = [
    # not authenticated
    path("signup/", views.SignUp.as_view(), name="sign_up"), #
    path("service_providers/", views.ServiceProviderCreate.as_view(), name="service_provider"), #
    
    # admin
    path("service_providers/check_account/<str:respond>/<int:provider_id>/"
        , views.accept_provider_account, name="accept_provider_account"),
    path("service_providers/all/", views.ServiceProviderList.as_view(), name="service_provider_list"), #
    
    # mixed: safe method for everybody, else owners and admins only
    path("service_provider/<int:pk>/", views.ServiceProviderRUD.as_view(), name="service_provider_rud"),
    
    # not authenticated
    path("email_confirmation/", views.email_confirmation, name="email_confirmation"), #
    path("resend_email_validation/", views.resend_email_validation, name="resend_email_validation"), #
    
    # authenticated
    path("accept_new_email/<str:token>", views.accept_email_change, name="accept_email_changing"),#
    path("change_email/", views.change_email, name="email_change"), #
    
    # authenticated
    path("check_password/", views.check_password, name="check_password"), #
    path("change_password/", views.change_password, name="change_password"),#
    
    # not authenticated
    path("reset_password/", views.reset_password, name="reset_password"),#
    path("enter_code/", views.enter_code, name="enter_code"),#
    path("new_password/", views.new_password, name="new_password"),#
    path("resend_code/", views.resend_code, name="resend_code"),#
    
    path("", views.list_all_users, name="all_users"), #
    path("<int:pk>/", views.UsersView.as_view(), name="specific_user"), #
    
    path("logout/", views.logout, name="log_out"),
    path('login/', views.LogIn.as_view(), name='login'), # tested
    path('refresh_token/', TokenRefreshView.as_view(), name='token_refresh'), # tested
    
    # 2FA
    path("send_2fa/", views.send_2FA_code, name="send_2FA_code"),
    path("resend_2fa/", views.resend_2fa_code, name="resend_2fa_code"),
    path("validate_2fa/<str:code>/", views.validate_2FA, name="validate_2FA"),
    
    # statistical endpoints
    path("stats/", views.active_users_stats, name="active_users_stats"),
    
    # search in users by email
    path("search/<str:search_term>/", views.search_users, name="search_users"),
]
