from django.utils import timezone
from django.conf import settings
from store_manager.models import Category
from .settings import SiteSettings


def inject_global_variables(request):
    common_settings = SiteSettings.load()
    global_variables = {}
    global_variables["now"] = timezone.now()
    global_variables["placeholder_image"] = common_settings.placeholder_image
    global_variables["shop_page"] = common_settings.shop_page
    global_variables["DEBUG"] = settings.DEBUG
    global_variables["popular_categories"] = Category.objects.filter(parent=None).all()
    global_variables["parent_categories"] = Category.objects.filter(parent=None).all()
    return global_variables
