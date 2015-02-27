from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"
    verbose_name = "Benutzerprofile"

    def ready(self):
        import signals 
