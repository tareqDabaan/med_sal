from django.db import models


class Category(models.Model):
    
    class CategoryNames(models.TextChoices):
        DOCTOR = ("DOCTOR", "Doctor")
        DENTAL = ("DENTAL", "Dental")
        OPTICS = ("OPTICS", "Optics")
        NUTRITIONIST = ("NUTRITIONIST", "Nutritionist")
        HOME_CARE = ("HOME_CARE", "Home_Care")
        PLASTIC_SURGERY = ("PLASTIC_SURGERY", "Plastic_Surgery")
        RADIOLOGIST = ("RADIOLOGIST", "Radiologist")
        AESTHETICS = ("AESTHETICS", 'Aesthetics')
        PHARMACY = ("PHARMACY", "Pharmacy")
        HOSTPITAL = ("HOSTPITAL", "Hostpital")
        LAB = ("LAB", "Lab")
        CLINIC = ("CLINIC", "Clinic")
    
    en_name = models.CharField(max_length=32, null=False, unique=True)
    ar_name = models.CharField(max_length=32, null=False) # unique=True
    parent = models.ForeignKey("category.Category", on_delete=models.CASCADE, null=True)
    
    def __str__(self) -> str:
        return f"{self.en_name}"
