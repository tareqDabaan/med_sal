from django.db import models

from users.models import Admins



class ContactUs(models.Model):
    name = models.CharField(max_length=255, null=False)
    mail = models.EmailField(max_length=127, null=False)
    message = models.TextField(null=False)
    read = models.BooleanField(default=False)
    read_by = models.ForeignKey(Admins, on_delete=models.PROTECT, related_name="contact_us", null=True)
    
    def __str__(self) -> str:
        return f"{self.name}, {self.mail}, {self.read}"
