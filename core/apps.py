from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def configure_sqlite(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA journal_mode = TRUNCATE;')
            cursor.execute('PRAGMA busy_timeout = 60000;')

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.contrib.auth.models import update_last_login
        from django.contrib.auth.signals import user_logged_in
        user_logged_in.disconnect(update_last_login, dispatch_uid='update_last_login')
