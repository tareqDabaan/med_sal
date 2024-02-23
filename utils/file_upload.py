from django.core.files.storage import FileSystemStorage

from uuid import uuid4
import os



class DeleteFilesMixin:
    
    def manage_uploaded_images(self):
        fs = FileSystemStorage()
        images_names = ""
        
        uploaded_images = self.uploaded_images()
        for image_obj in uploaded_images:
            files_names = self.get_files_names(fs)
            unique_name = self.check_redundent(image_obj.name, files_names)
            images_names += f" {fs.base_url}{unique_name}"
            fs.save(unique_name, image_obj)
            
        return images_names[1:]
    
    def check_redundent(self, image_name, files_names):
        new_name, new_extension = uuid4().hex, image_name.split(".")[1]
        new_image_name = f"{new_name}.{new_extension}"
        if new_image_name in files_names:
            return self.check_redundent(image_name, files_names)
        return new_image_name
    
    def get_files_names(self, fs: FileSystemStorage):
        return fs.listdir(fs.location)[1]
    
    def uploaded_images(self):
        return self.request.FILES.getlist("images")
    
    
    def delete_files(self, obj):
        fs = FileSystemStorage()
        location = fs.location
        
        images_names = obj.images.split(" ")
        for image in images_names:
            try:
                os.remove(f"{location}\{image[6:]}")
            except FileNotFoundError:
                pass