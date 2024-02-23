from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
