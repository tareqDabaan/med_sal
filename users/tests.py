from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.test import APIClient

from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase
from mixer.backend.django import mixer
import pytest

from service_providers.models import ServiceProvider
from category.models import Category

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestUserModels(TestCase):
    @classmethod
    def setUp(self) -> None:
        self.user_data = {
            "email": "maamoun.haj.najeeb@gmail.com"
            , "password": "17AiGz48rhe"
            , "user_type": "USER"
            , "is_active": True
            , "phone": "+963932715313"
        }
        
        self.category_data = {
            "ar_name": "أطباء"
            , "en_name": "Doctors"
        }
        
        self.service_provider_data = {
            "bank_name": "Albaraka"
            , "business_name": "Django On the Backend"
            , "iban": "i1b2a3n4"
            , "swift_code": "s1w2i3f4t5"
        }
        
        self.user = User.objects.create_user(**self.user_data)
        self.category = Category.objects.create(**self.category_data)
        self.service_provider = ServiceProvider.objects.create(
            **self.service_provider_data, category=self.category, user=self.user)
    
    @given(some_value=st.text(max_size=15))
    def test_create_user(self, some_value):
        assert self.user.email != some_value
    
    def test_create_category(self):
        assert self.category.ar_name == "أطباء"
        assert self.category.en_name == "Doctors"
    
    def test_create_service_provider(self):
        assert self.service_provider.user == self.user


class TestUsersAPI(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        
        self.user_data = {
            "email": "maamoun.haj.najeeb@gmail.com"
            , "password": "17AiGz48rhe"
            , "password2": "17AiGz48rhe"
            , "user_type": "USER"
            , "is_active": True
            , "phone": "+963932715313"
        }
        
        self.group = Group.objects.create(name="USER")
    
    # @given()
    def test_user_api_create(self):
        response = self.client.post(
            path="/api/v1/users/signup/"
            , data=self.user_data
            , format="json")
            # headers={"Accept-Language": "ar"}
        
        assert response.json != None
        assert response.status_code == 201
        
    def test_user_login(self):
        self.client.logout()
        
        data = self.user_data.copy()
        data.pop("password2")
        User.objects.create_user(**data)
        
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "17AiGz48rhe"}
            , format="json")
        response_data = response.json()
        
        assert response.status_code == 200
        assert response_data["user_type"] == "USER"
        
    def test_refresh_token(self):
        self.client.logout()
        
        data = self.user_data.copy()
        data.pop("password2")
        User.objects.create_user(**data)
        
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "17AiGz48rhe"}
            , format="json")
        response_data = response.json()
        
        assert response.status_code == 200
        
        refresh_response = self.client.post(
            path="/api/v1/users/refresh_token/"
            , data={"refresh": response_data["refresh"]}
            , format="json")
        
        assert refresh_response.status_code == 200


class TestUsersAPIView(TestCase):
    def setUp(self) -> None:
        Group.objects.create(name="USER")
        Group.objects.create(name="ADMIN")
        
        self.user_data = {
            "user_type": "USER"
            , "password": "17AiGz48rhe"
            , "email": "maamoun.h.najeeb@gmail.com"
            , "is_active": True
            , "phone": "+963932715312"}
        
        self.admin_data = {
            "user_type": "ADMIN"
            , "password": "17AiGz48rhe"
            , "email": "maamoun.haj.najeeb@gmail.com"
            , "is_active": True
            , "phone": "+963932715313"}
        
        self.client = APIClient()
    
    def create_admin(self):
        User.objects.create_user(**self.admin_data)
    
    def create_user(self):
        User.objects.create_user(**self.user_data)
    
    def login(self):
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "17AiGz48rhe"}
            , format="json")
        
        return response.json()["refresh"]
    
    def test_list_users_api(self):
        self.create_admin()
        self.create_user()
        
        token = self.login()
        
        # self.client.credentials(HTTP_AUTHORIZATION=f"JWT {token}")
        response = self.client.get(path="api/v1/users/")
        
        assert response.status_code == 200
        # assert len(response.json()) == 2
