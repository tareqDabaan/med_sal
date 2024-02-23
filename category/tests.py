from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from hypothesis.extra.django import TestCase

from .models import Category


Users = get_user_model()

def user_model_create(user_type: str):
    group_data = {"name": user_type}
    
    user_data = {
        "email": "maamoun.haj.najeeb@gmail.com"
        , "password": "sv_gtab101enter"
        , "phone": "+963932715313"
        , "user_type": user_type
        , "is_active": True
    }
    
    if user_type == "ADMIN":
        user_data["is_staff"] = True
    
    Group.objects.create(**group_data)
    user = Users.objects.create_user(**user_data)
    
    return user

def get_access_token(client: APIClient, user_type: str):
    user_model_create(user_type)
    
    response = client.post(
        path="/api/v1/users/login/"
        , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "sv_gtab101enter"}
        , format="json")
    
    return response.json().get("access")


class TestCreateAPI(TestCase):
    def setUp(self) -> None:
        self.category_data = {"en_name": "Doctors", "ar_name": "أطباء"}
        self.client = APIClient()
    
    def test_create_category(self):
        access_token = get_access_token(self.client, 'ADMIN')
        
        response = self.client.post(
            path="/api/v1/category/create/"
            , data=self.category_data
            , format="json"
            , headers={"Authorization": f"JWT {access_token}"})
        
        response_data = response.json()
        
        assert response.status_code == 201
        
        assert response_data["en_name"] == "Doctors"
        assert response_data["ar_name"] == "أطباء"
        assert response_data["ar_name"] != "Doctors"
        assert response_data["en_name"] != "أطباء"
    
    def login(self):
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "sv_gtab101enter"}
            , format="json")
        
        return response.json().get("access")


class TestListAndRetrieveAPI(TestCase):
    def setUp(self) -> None:
        self.category_data = {"en_name": "Doctors", "ar_name": "أطباء"}
        self.client = APIClient()
    
    def test_valid_retrieve(self):
        self.create_category()
        
        response = self.client.get(path="/api/v1/category/1/", headers={"Accept-Language": "ar"})
        instance_data = response.json()[0]
        
        assert instance_data["name"] == "أطباء"
    
    def test_invalid_retrieve(self):
        self.create_category()
        
        response = self.client.get(path="/api/v1/category/2/")
        assert response.status_code == 404
    
    def test_valid_list(self):
        self.create_category()
        
        response = self.client.get(path="/api/v1/category/", headers={"Accept-Language": "ar"})
        queryset_data = response.json()
        
        assert len(queryset_data) == 1
    
    def test_invalid_list(self):
        response = self.client.get(path="/api/v1/category/", headers={"Accept-Language": "ar"})
        queryset_data = response.json()
        
        assert len(queryset_data) == 0
    
    def create_category(self):
        access_token = get_access_token(self.client, "ADMIN")
        
        self.client.post(
            path="/api/v1/category/create/", data=self.category_data
            , format="json", headers={"Authorization": f"JWT {access_token}"}
            )
    
    def login(self):
        response = self.client.post(
            path="/api/v1/users/login/"
            , data={"email": "maamoun.haj.najeeb@gmail.com", "password": "sv_gtab101enter"}
            , format="json")
        
        return response.json().get("access")


class TestUpdateAndDestroyAPI(TestCase):
    def setUp(self) -> None:
        self.category_data = {"en_name": "Doctors", "ar_name": "أطباء"}
        self.client = APIClient()
    
    def test_invalid_update_category(self):
        self.create_category()
        
        response = self.client.patch(
            path="/api/v1/category/update/2/"
            , headers={"Authorization": f"JWT {get_access_token(self.client, 'ADMIN')}"})
        assert response.status_code == 404
    
    def test_update_category(self):
        self.create_category()
        
        response = self.client.patch(
            path="/api/v1/category/update/1/"
            , headers={"Authorization": f"JWT {get_access_token(self.client, 'ADMIN')}"})
        response_data = response.json()
        
        assert response_data.get("en_name") == "Doctors"
        assert response_data.get("ar_name") == "أطباء"
        assert response.status_code == 200
        
    def test_destroy_category(self):
        self.create_category()
        
        response = self.client.delete(
            path="/api/v1/category/destroy/1/"
            , headers={"Authorization": f"JWT {get_access_token(self.client, 'ADMIN')}"})
        assert response.status_code == 204
        
    def test_invalid_destroy_category(self):
        self.create_category()
        
        response = self.client.delete(
            path="/api/v1/category/destroy/6/"
            , headers={"Authorization": f"JWT {get_access_token(self.client, 'ADMIN')}"})
        assert response.status_code == 404
    
    def create_category(self):
        Category.objects.create(**self.category_data)


class TestDeniedUser(TestCase):
    def setUp(self) -> None:
        self.category_data = {"en_name": "Developers", "ar_name": "مطورون"}
        
        self.client = APIClient()
    
    def test_user_update(self):
        self.create_category()
        
        response = self.client.patch(
            path="/api/v1/category/update/1/", format="json"
            , headers={"Authorization": f"JWT {get_access_token(self.client, 'USER')}"}
        )
        
        assert response.status_code == 403
    
    def create_category(self):
        Category.objects.create(**self.category_data)
