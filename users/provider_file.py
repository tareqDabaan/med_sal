from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os, uuid
from datetime import datetime


MEDIA_FOLDER = settings.MEDIA_ROOT


class FileMixin():
    
    def upload(self, file_obj):
        fs = FileSystemStorage(location=self.foldering_cliche())
        extension = file_obj.name.split(".")[1]
        file_name = self.change_filename(extension)
        fs.save(file_name, file_obj)
        print(file_name)
        return file_name
        
    def change_filename(self, extension) -> str:
        file_name = f"{uuid.uuid4().hex}.{extension}"
        redundent_name = self.check_redundent_names(file_name)
        if redundent_name:
            return self.change_filename()
        return file_name
    
    def check_redundent_names(self, file_name: str) -> bool:
        fs = FileSystemStorage(location=self.foldering_cliche())
        folder_cliche = self.foldering_cliche()
        files = fs.listdir(path=folder_cliche)[1]
        if file_name in files:
            return True
        return False
    
    def foldering_cliche(self):
        year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
        path = os.path.join(MEDIA_FOLDER, "service_providers", str(year), str(month), str(day))
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    def dir_filenames(self, files, file_name): #
        if file_name in files:
            return True
        return False
    
    def file_obj(self):
        pass
    
    def file_path(self):
        pass
    
    
    def delete(self):
        pass