from django import template
from django.utils import timezone
import json
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def site_root(context):
    request = context.get("request")
    if request:
        return f"{request.scheme}://{request.get_host()}/"
    return "/"


@register.simple_tag
def static_timestamp():
    from django.conf import settings
    if settings.DEBUG:
        return f"?v={timezone.now().timestamp()}"
    return ""


@register.simple_tag(takes_context=True)
def wishlisted_products(context):
    request = context.get("request")
    product_ids = []
    if request and request.user and request.user.is_authenticated:
        product_ids = list(request.user.wishlisted_products.values_list("id", flat=True))
    return mark_safe(json.dumps(product_ids))
