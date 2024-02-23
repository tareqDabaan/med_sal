from django.db import models



class Notification(models.Model):
    
    class Types(models.TextChoices):
        User = ("User", "User")
        System = ("System", "System")
        Service_Provider = ("Service_Provider", "Service_Provider")
    
    sender = models.CharField(max_length=255)
    sender_type = models.CharField(choices=Types.choices, max_length=32, null=False)
    receiver = models.CharField(max_length=255)
    receiver_type = models.CharField(choices=Types.choices, max_length=32, null=False)
    read = models.BooleanField(default=False)
    ar_content = models.CharField(max_length=1023, null=False)
    en_content = models.CharField(max_length=1023, null=False)
    created_at = models.DateTimeField(auto_now_add=True) # null to be False
    
    def __str__(self) -> str:
        return f"{self.sender} -> {self.receiver}, read: {self.read}"
