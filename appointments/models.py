from django.conf import settings
from django.db import models

from services.models import Service



class Appointments(models.Model):
    
    class AppointmentStatus(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=False, related_name="appointments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name="appointments")
    diagonsis = models.TextField(null=True)
    from_time = models.TimeField(null=False)
    to_time = models.TimeField(null=False)
    date = models.DateField(null=False)
    status = models.CharField(
        max_length=15, choices=AppointmentStatus.choices, null=False
        , default=AppointmentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.service.en_title}, user: {self.user.email}"


class RejectedAppointments(models.Model):
    appointment = models.OneToOneField(
        Appointments, on_delete=models.CASCADE, null=False, related_name="rejected_appointments")
    reason = models.TextField(null=False)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.appointment.service.en_title}, read from admin: {self.read}"
