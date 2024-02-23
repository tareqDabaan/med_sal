from django.contrib.auth.models import (
        AbstractBaseUser, BaseUserManager, PermissionsMixin
        )
from django.contrib.auth.hashers import make_password
from django.db.models.query import QuerySet
from django.conf import settings
from django.db import models

from typing import Any

from .models_helpers import get_image_path


class MyUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(
            email=self.normalize_email(email)
            , password=make_password(password)
            , **kwargs)
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)
        
        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(**kwargs)
    
    def get_by_natural_key(self, email: None) -> Any:
        email = self.normalize_email(email)
        return self.get(**{self.model.USERNAME_FIELD: email})


class Users(AbstractBaseUser, PermissionsMixin):
    
    class Types(models.TextChoices):
        SERVICE_PROVIDER = ("SERVICE_PROVIDER", "Service_Provider")
        SUPER_ADMIN = ("SUPER_ADMIN", "Super_Admin")
        ADMIN = ("ADMIN", "Admin")
        USER = ("USER", "User")
    
    email = models.EmailField(max_length=128, unique=True, null=False)
    phone = models.CharField(max_length=16, unique=True, null=False)
    image = models.ImageField(
        upload_to=get_image_path, default="defaults/default_profile.jpg", null=True)
    
    base_type = Types.USER
    user_type = models.CharField(
        max_length=16, choices=Types.choices, default=base_type)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    REQUIRED_FIELDS = ["user_type"]
    USERNAME_FIELD = "email"
    
    objects = MyUserManager()
    
    class Meta:
        verbose_name = "Users"
        
    def __str__(self) -> str:
        return str(self.email)
    
    @property
    def re_password(self):
        return 


class SuperAdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.SUPER_ADMIN)


class SuperAdmins(Users):
    base_type = Users.Types.SUPER_ADMIN
    super_admins = SuperAdminsManager()
    
    class Meta:
        proxy = True
        verbose_name = "SuperAdmin"
        verbose_name_plural = "SuperAdmin"


class AdminsManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        result = super().get_queryset()
        return result.filter(user_type=Users.Types.ADMIN)


class Admins(Users):
    base_type = Users.Types.SUPER_ADMIN

    admins = AdminsManager()

    class Meta:
        proxy = True
        verbose_name = "Admins"


class UserIP(models.Model):
    """
    for languages [ip_address, language preference]
    """
    ip_address = models.CharField(max_length=32, primary_key=True, null=False)
    language_code = models.CharField(max_length=8, null=False)
    
    def __str__(self) -> str:
        return f"{self.ip_address} => {self.language_code}"


class EmailConfirmation(models.Model):
    """
    to activate user via code
    """
    user_id = models.BigIntegerField(primary_key=True)
    ip_address = models.CharField(max_length=32, unique=True, null=False)
    email = models.EmailField(max_length=64, unique=True, null=False)


class EmailChange(models.Model):
    """
    to activate new email
    """
    user_id = models.BigIntegerField(primary_key=True)
    token = models.CharField(max_length=16, unique=True)
    new_email = models.EmailField(max_length=64, unique=True)


class PasswordReset(models.Model):
    code = models.CharField(max_length=6, unique=True, null=False)
    ip_address = models.CharField(max_length=32, unique=True, null=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)
