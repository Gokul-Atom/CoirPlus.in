from django import template
from django.utils import timezone

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
