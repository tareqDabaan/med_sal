from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError, BaseCommand, CommandParser
from django.contrib.auth.hashers import make_password

from users.models import SuperAdmins


class Command(BaseCommand):
    
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--email", type=str)
        parser.add_argument("--password", type=str)
    
    def handle(self, *args, **options):
        super_user = SuperAdmins.objects.create(
            email=options.get("email")
            , password=make_password(options.get("password"))
            , is_superuser=True, is_staff=True
            , user_type=SuperAdmins.Types.SUPER_ADMIN)
        
        self.stdout.write(f"{super_user} created")
