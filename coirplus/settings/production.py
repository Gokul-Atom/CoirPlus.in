from .base import *

DEBUG = False

# ManifestStaticFilesStorage is recommended in production, to prevent
# outdated JavaScript / CSS assets being served from cache
# (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

SECRET_KEY = "django-insecure-=zk3+#yu72*iy3!b=9_$r@ovc%25kv(sw8oh#fyfx0g=pkvh33"

BASE_DIR = "/home/lalitsunco/public_html"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

ALLOWED_HOSTS = [
    "www.coirplus.in",
    "coirplus.in",
    ]

try:
    from .local import *
except ImportError:
    pass
