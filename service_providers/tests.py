# from django.test import TestCase
# from service_providers.models import ServiceProvider  # Adjust these imports as needed
# from category.models import Category
# from users.models import Users, Admins


# class ServiceProviderApprovalTest(TestCase):
#     def test_service_provider_approval(self):

#         admin = Admins.objects.create(email = 'admin@gmail.com')

#         category = Category.objects.create(name = 'Doctor')

#         user = Users.objects.create(email="provider@gmail.com")

#         service_provider = ServiceProvider.objects.create(user = user, category = category)

#         service_provider.approved_by = admin
#         service_provider.save()

#         approved_admin = service_provider.approved_by

#         self.assertEqual(approved_admin, admin)
