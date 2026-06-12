import os
import logging
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youimmo.settings')
django.setup()

from django.conf import settings
settings.DEBUG = True

# Activer le log des requêtes SQL dans la console
logger = logging.getLogger('django.db.backends')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

from django.contrib.auth.models import User
u = User.objects.first()
print('--- Récupération du User OK, début du save() ---')
u.save()
print('--- save() OK ---')
