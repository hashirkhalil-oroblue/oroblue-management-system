"""
WSGI config for oroblue_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Ensure the correct settings module is used (can be overridden by environment variable)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oroblue_project.settings")

# Optional: log WSGI startup (helps debugging on Render)
sys.stdout.write("WSGI application loaded with settings: {}\n".format(
    os.environ["DJANGO_SETTINGS_MODULE"]
))

application = get_wsgi_application()

