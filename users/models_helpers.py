from uuid import uuid4
import datetime, os


def get_image_path(instance, filename):
    extension = os.path.splitext(filename)[1]
    new_filename = uuid4().hex + extension
    
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    day = datetime.datetime.now().day
    return os.path.join(f"profile_images/{year}/{month}/{day}", new_filename)
