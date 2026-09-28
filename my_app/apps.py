from django.apps import AppConfig


class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'my_app'
    def ready(self):
        import my_app.signals

def ready(self):
        groups = ['Participant', 'Manager']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)