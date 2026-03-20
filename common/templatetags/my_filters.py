from django import template

register = template.Library()


@register.filter
def first_line(value:str):
    if value:
        return value.split("\n")[0]


@register.filter
def splitlines(value:str):
    if value:
        return value.replace("\r", "").split("\n")


@register.filter
def get_item(dict:dict, key:str):
    if dict:
        return dict.get(key)


@register.filter
def widget_type(field):
    return field.field.widget.__class__.__name__


@register.filter
def star_rating_classes(rating:int, max: int):
    class_list = []
    for i in range(1, max + 1):
        class_list.append("bi bi-star-fill" if i <= rating else "bi bi-star")
    return class_list


@register.filter
def thumbnail(product_id:int):
    from store_manager.models import ProductVariation
    from django.shortcuts import get_object_or_404
    variation = get_object_or_404(ProductVariation, id=product_id)
    return None


@register.filter
def add_class(field, css_class):
    """Add CSS class to Django form field"""
    attrs = field.field.widget.attrs
    classes = attrs.get('class', '').split()
    classes.append(css_class)
    attrs['class'] = ' '.join(classes)
    return field
