from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Import inside ready() to avoid AppRegistryNotReady errors
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError, ProgrammingError

        try:
            User = get_user_model()

            # Create admin only if it does not exist
            if not User.objects.filter(email="official.mercymbaka@gmail.com").exists():
                User.objects.create_superuser(
                    email="official.mercymbaka@gmail.com",
                    password="49474918",  # change later in production
                )

        except (OperationalError, ProgrammingError):
            # Prevent crash during migrations / first deploy
            pass