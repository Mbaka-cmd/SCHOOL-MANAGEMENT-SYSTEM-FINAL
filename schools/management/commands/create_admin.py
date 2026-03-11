from django.core.management.base import BaseCommand
from accounts.models import User
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        email = os.environ.get("ADMIN_EMAIL", "official.mercymbaka@gmail.com")
        password = os.environ.get("ADMIN_PASSWORD", "MercyAdmin2026!")
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name="Mercy",
                last_name="Mbaka"
            )
            self.stdout.write("Superuser created!")
        else:
            self.stdout.write("Already exists.")
