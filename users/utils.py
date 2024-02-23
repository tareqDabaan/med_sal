from django.utils import timezone

from uuid import uuid4
import os

def unique_image_name(instance, filename: str):
    time = timezone.now()
    ext = filename.split(".")[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join(
        "profile_images"
        , time.strftime("%Y/%m/%d")
        , filename)


def find_image():
    pass