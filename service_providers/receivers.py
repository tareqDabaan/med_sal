from django.dispatch import receiver
from django.core.mail import send_mail
from .models import UpdateProfileRequest
from .signals import update_profile_request_created

@receiver(update_profile_request_created)
def handle_profile_update_request(sender, **kwargs):
    request = kwargs['sender']

    # Get the updated profile data
    updated_data = request.updated_data
