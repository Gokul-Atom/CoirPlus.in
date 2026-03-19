from django.apps import AppConfig


class StoreManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store_manager'

    def ready(self):
        import store_manager.signals
