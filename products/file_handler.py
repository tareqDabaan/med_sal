from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest
from django.conf import settings

import os, uuid

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL


class UploadImages:
    def __init__(self, request: HttpRequest) -> None:
        self.protocol = "https" if request.is_secure() else "http"
        self.host = request.get_host()
        # self.port = request.get_port() # maybe we need in the production
    
    def upload_files(self, folder_name: str, files: list[InMemoryUploadedFile]):
        FS = FileSystemStorage()
        
        self._check_ratio_and_size(files)
        FS.location = os.path.join(FS.location, folder_name)
        files = self._change_files_names(files)
        self._upload_files(FS, files)
        files_names = self._get_absolute_url(files, folder_name)
        return files_names
    
    def _upload_files(self, FS: FileSystemStorage, files: list[InMemoryUploadedFile]):
        for file_obj in files:
            FS.save(file_obj.name, file_obj)
    
    def _get_absolute_url(self, files: list[InMemoryUploadedFile], folder_name: str):
        files_names = []
        for file_obj in files:
            name = f"{self.protocol}://{self.host}{MEDIA_URL}{folder_name}/{file_obj.name}"
            files_names.append(name)
        
        return ",".join(files_names)
    
    def _change_files_names(self, files: list[InMemoryUploadedFile]):
        for file_obj in files:
            file_obj.name = uuid.uuid4().hex + "." + file_obj.name.split(".")[1]
            
        return files
    
    def _check_ratio_and_size(self, files: list[InMemoryUploadedFile]):
        for file_obj in files:
            # self._check_ratio(file_obj)
            self._check_size(file_obj)
    
    def _check_size(self, file_obj: InMemoryUploadedFile):
        if file_obj.size / 1024 / 1024 > 5:
            return "sorry but file size should be lower than 5 Mega Bytes"
    
    def _check_ratio(self, file_obj: InMemoryUploadedFile):
        if file_obj.width > 1280 and file_obj.height > 720:
            return "sorry but file ratio should be less than 1280 for the width and less than 720 for height"


class DeleteFiles:
    
    def delete_files(self, paths: str):
        paths = paths.split(",")
        
        for path in paths:
            
            def delete_file(path):
                try:
                    os.remove(os.path.join(MEDIA_ROOT, path[4], path[5]))
                    print("File Deleted")
                except:
                    print("No such file in this path")
            
            delete_file(path.split("/"))
            