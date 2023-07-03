from django.apps import AppConfig

class GpserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.GPService'

    def ready(self):
        import apps.GPService.signals