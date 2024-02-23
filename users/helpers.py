from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpRequest
from django.conf import settings

from datetime import datetime
import os, random, uuid


Users = get_user_model()


MEDIA_FOLDER = settings.MEDIA_ROOT


class FileMixin():
    
    def upload(self, file_obj, folder_name: str):
        if file_obj.size / 1024 / 1024 > 5:
            return "Sorry, but file you've uploaded is more than 5 mega byte"
        
        if type(file_obj) != InMemoryUploadedFile:
            return f"Sorry, but you should updload a file not a {type(file_obj)}"
        
        fs = FileSystemStorage(location=self.foldering_cliche(folder_name))
        extension = file_obj.name.split(".")[1]
        
        change_filename = lambda extension: f"{uuid.uuid4().hex}.{extension}"
        file_name = change_filename(extension)
        
        fs.save(file_name, file_obj)
        return f"service_providers/{file_name}"
    
    def foldering_cliche(self, folder_name: str) -> str:
        path = os.path.join(MEDIA_FOLDER, folder_name)
        return path


class SendMail:
    
    def __init__(self, request: HttpRequest, to: str, view: str, out: bool = False) -> None:
        self.to, self.request = to, request
        self.subject = "Med Sal Email Confirmation"
        self.view = view
        self.out = out
    
    def generate_token(self):
        token = ""
        for _ in range(16):
            token += str(random.randint(0, 9))
        
        return token
    
    def get_content(self):
        protocol = "https" if self.request.is_secure() else "http"
        host = self.request.get_host()
        self.token = self.generate_token()
        
        if self.out:
            full_path = f"{protocol}://{host}{self.view}"
        else:
            full_path = f"{protocol}://{host}{self.view}{self.token}"
        
        return f"please use this link to verify your account: \n {full_path}"
        
    def send_mail(self):
        content = self.get_content()
        send_mail(
            subject=self.subject
            , message=content
            , from_email="med-sal-adminstration@gmail.com"
            , recipient_list=[self.to, ])



def activate_user(id: int):
    user_instance: Users = Users.objects.get(id=id)
    user_instance.is_active = True
    user_instance.save()


def change_user_email(id: int, new_email: str):
    user_instance: Users = Users.objects.get(id=id)
    user_instance.email = new_email
    user_instance.save()


def set_password(user: Users, new_pwd: str):
    user.set_password(new_pwd)
    user.save()


def generate_code() -> str:
    code = ""
    for _ in range(6):
        code += str(random.randint(0, 9))
    
    return code


def get_file_path(filename):
    extension = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + extension
    
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    day = datetime.datetime.now().day
    return f"profile_images/{year}/{month}/{day}", new_filename


def upload_file(image_obj):
    image_full_path, image_new_name = get_file_path(image_obj.name)
    fs = FileSystemStorage(location=image_full_path)
    fs.save(image_new_name, image_obj)
    
    return image_new_name


def delete_image(path):
    if os.path.exists(path):
        os.remove(path)
        print("Image Deleted Successfully")
    else:
        print("No Such File at This Path")
