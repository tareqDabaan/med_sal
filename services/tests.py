# from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
# from django.test import TestCase, modify_settings

# from django.contrib.auth import get_user_model

# from service_providers.models import ServiceProvider
# from category.models import Category
# from users.models import Users
# Users = get_user_model()


# class MyTests(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user_data = {
#             "email" : "maamounnajeeb@gmail.com"
#             , "password":"sv_gtab101enter"
#             , "is_active": True
#             , "phone": "+963959539503"
#             , "user_type": Users.Types.USER
#         }
        
#         cls.superuser_data = {
#             "email" : "maamounnajeebsuper@gmail.com"
#             , "password":"sv_gtab101enter"
#             , "is_active": True
#             , "is_superuser": True
#             , "is_staff" : True
#             , "phone": "+963932715313"
#             , "user_type": Users.Types.SUPER_ADMIN
#         }
        
#         cls.api_client = APIClient()
    
#     def create_category(self):
#         return Category.objects.create(
#             ar_name="أطباء", en_name="Doctors")
    
#     def create_user(self):
#         return Users.objects.create_user(**self.user_data)
    
#     def create_service_provider(self):
#         data = {
#             "user": self.create_user()
#             , "category": self.create_category()
#             , "business_name": "Django for Experts"
#             , "iban": "i1b2a3n4"
#             , "swift_code": "s1w2i3f4t5"
#             , "bank_name": "Albarka"
#         }
        
#         return ServiceProvider.objects.create(**data)
    
#     # def test_login(self):
#     #     user = self.create_user()
#     #     response = self.client.post("api/v1/users/login/"
#     #         , **{"email": user.email, "password": "sv_gtab101enter"}
#     #         , format="json")
        
#     #     print(response)
        
#     #     self.assertEqual(200, 200)
    
#     @modify_settings(MIDDLEWARE={"remove": 'core.middleware.language_middleware.language'})
#     def test_create_provider_location(self):
#         data = {
#             "service_provider": self.create_service_provider,
#             "opening": "08:00:00",
#             "closing": "19:00:00",
#             "crew": "Maamoun Haj Najeeb: second doctor, Tareq Dabaan: first doctor",
#             "location": "POINT(-90.432432 2.345945)"
#         }
        
#         service_provider = self.create_service_provider()
#         self.api_client.force_authenticate(user=service_provider.user)
#         request = self.api_client.post(
#             "/api/v1/service_providers/locations/create/"
#             , **data, format="json")
        
        
#         self.assertEqual(request, 201)