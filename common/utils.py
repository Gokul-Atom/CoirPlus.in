from django.apps import apps
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.contrib.messages.storage.fallback import FallbackStorage

from .settings import SiteSettings
from .models import SiteSettings


# class UniqueMessageStorage(FallbackStorage):
#     def add(self, level, message, extra_tags='', fail_silently=False):
#         if message not in [m.message for m in self]:
#             super().add(level, message, extra_tags)


def get_model(app: str, model: str):
    return apps.get_model(app, model)


def get_placeholder_image():
    site_settings = SiteSettings.load()
    return site_settings.placeholder_image


# def admin_display(*args, **kwargs):
#     Category = apps.get_model("store_manager", "Category")
#     Product = apps.get_model("store_manager", "Product")
#     obj = kwargs["obj"]
#     display_type = kwargs["display_type"]
#     sep = kwargs["sep"]
#     html = f"{obj.name}"
#     if type(obj) == Category:
#         category = []
#         children = []
#         category_suffix = "Sub-categories"
#         children_suffix = "Products"
#         if obj.parent:
#             parent = obj.parent.name
#             html += f"<br><small style='font-weight: 400'><strong>Parent Category:</strong> {parent}</small>"
#         else:
#             category = obj.children.all()
#         children = obj.products.all()
#     if display_type == "full":
#         html += f"<br><small style='font-weight: 400'><strong>{category_suffix}:</strong> {sep.join(category)}</small>" if category else ""
#         html += f"<br><small style='font-weight: 400'><strong>{children_suffix}:</strong> {sep.join(children)}</small>" if children else ""
#     else:
#         html += f"<br><small style='font-weight: 400'>{len(category)} {category_suffix}</small>" if category else ""
#         html += f"<br><small style='font-weight: 400'>{len(children)} {children_suffix}</small>" if children else ""
#     return html


# def url_params_to_string(request, skip_page=True):
#     url_params_list = []
#     keys = request.GET.keys()
#     for key in keys:
#         if skip_page and key == "page":
#             continue
#         params = request.GET.getlist(key)
#         for param in params:
#             url_params_list.append(f"{key}={param}")
#     return "&".join(url_params_list)


# def get_pagination_object(object_list, per_page, page):
#     search_results = None
#     page_range = None
#     paginator = Paginator(object_list, per_page)
#     try:
#         search_results = paginator.page(page)
#         page_range = paginator.get_elided_page_range(number=page, on_each_side=2, on_ends=1)
#     except PageNotAnInteger:
#         search_results = paginator.page(1)
#         page_range = paginator.get_elided_page_range(number=1, on_each_side=2, on_ends=1)
#     except EmptyPage:
#         search_results = paginator.page(paginator.num_pages)
#         page_range = paginator.get_elided_page_range(number=paginator.num_pages, on_each_side=2, on_ends=1)
#     return search_results, page_range


# def get_related_products(product):
#     Product = get_model("store_manager", "Product")
#     related_products = []
#     unique_related_products = []
#     product_ids = []
#     # attributes = product.attributes.all()
#     related_products.extend(Product.objects.filter(categories__in=product.categories.all()).distinct().exclude(pk=product.pk))
#     # related_products.extend(Product.objects.filter(models.Q(attributes__in=attributes) | models.Q(product_variations__attributes__in=attributes)).distinct().exclude(pk=product.pk))
#     for product in related_products:
#         if product.id not in product_ids:
#             product_ids.append(product.id)
#             unique_related_products.append(product)
#     return unique_related_products[:8]


# def filter_products(request):
#     Product = get_model("store_manager", "Product")
#     filtered_products = Product.objects.all()
#     filter_slugs = {}
#     keys = request.GET.keys()
#     print(keys)
#     if "categories" in keys:
#         collection_slugs = request.GET.getlist("categories")
#         filtered_products = filtered_products.filter(categories__slug__in=collection_slugs).distinct()
#     print(filtered_products)
#     for key in keys:
#         if key == "categories" or key == "q" or key == "page":
#             continue
#         filter_slugs[key] = request.GET.getlist(key)
#     print(filter_slugs)
#     if filter_slugs:
#         for key in filter_slugs:
#             # filtered_products = filtered_products.filter(models.Q(product_variations__attributes__slug__in=filter_slugs[key]) | models.Q(models.Q(attributes__slug__in=filter_slugs[key]))).distinct()
#             filtered_products = filtered_products.filter(product_variations__attributes__slug__in=filter_slugs[key]).distinct()
#     return filtered_products


# def get_all_filters_for_product(product):
#     variants = product.product_variations.all()
#     temp_filters = dict()
#     items_in_pack = set()
#     for variant in variants:
#         for attribute in variant.attributes.all():
#             product_attribute = attribute.attribute
#             if product_attribute in temp_filters.keys():
#                 temp_filters[product_attribute].add(attribute)
#             else:
#                 temp_filters[product_attribute] = {attribute}
#         items_in_pack.add(variant.items_in_pack)
#     # Order of filter values is maintained below
#     filters = {}
#     for filter_category, filter_values in temp_filters.items():
#         filters[filter_category] = [value for value in filter_category.attribute_values.all() if value in filter_values]
#     return variants, filters, items_in_pack    


# def update_recently_viewed(request, product=None):
#     RecentlyViewed = get_model("account_manager", "RecentlyViewed")
#     Product = get_model("store_manager", "Product")
#     if request.user.is_authenticated:
#         if product:
#             recently_viewed, created = RecentlyViewed.objects.get_or_create(user=request.user, product=product)
#             recently_viewed.save()
#         return [product.product for product in RecentlyViewed.objects.filter(user=request.user).all()]
#     else:
#         recently_viewed:list = request.session.get("recently_viewed", [])
#         if product:
#             product_id = product.id
#             if recently_viewed and product_id in recently_viewed:
#                 product_index = recently_viewed.index(product_id)
#                 product_id = recently_viewed.pop(product_index)
#             recently_viewed.append(product_id)
#             request.session["recently_viewed"] = recently_viewed
#         return [Product.objects.get(pk=product_id) for product_id in recently_viewed]


def validate_basket(basket, request):
    errors = []
    for item in basket.items.all():
        if not item.product.is_stock_available(item.quantity):
            stock_display = item.product.stock_display
            if stock_display > 0:
                errors.append(f'Adjust the checkout quantity for <strong>{item.product.product.name}</strong> to <strong>"<= {stock_display}"</strong>. Only <strong><u>{stock_display}</u></strong> left in stock!')
            else:
                errors.append(f"Yikes! <strong>{item.product.product.name}</strong> is out of stock!")
    if errors:
        raise ValidationError(errors)
    if request and request.user.is_authenticated:
        basket.update(request)

def schedule_order_email(order, debug=True):
    # import traceback
    # traceback.print_stack()
    # import inspect
    # print(inspect.currentframe().f_back.f_code)
    # return
    # from store_manager.models import Order
    # order = Order.objects.filter(ref="2025-00067").first()
    # email_settings = EmailSettings.load()
    settings = SiteSettings.load()
    # site_settings = SiteSettings.load()
    ScheduledMessage = get_model("common", "ScheduledMessage")
    # if not email_settings.enable_email:
        # return
    # connection = get_connection(
    #     backend="django.core.mail.backends.smtp.EmailBackend",
    #     host=email_settings.email_host,
    #     port=email_settings.email_port,
    #     username=email_settings.email_host_user,
    #     password=email_settings.emai_host_password,
    #     use_tls=email_settings.email_use_tls,
    #     use_ssl=email_settings.email_use_ssl,
    #     fail_silently=False,
    # )
    order_status = order.status
    subject = None
    if order_status == "NEW":
        subject = "Order Placed"
    elif order_status == "CREATED":
        subject = "Order Paid"
    elif order_status == "HOLD":
        subject = None
    elif order_status == "FAILED":
        subject = "Order Failed"
    elif order_status == "CANCELLED":
        subject = "Order Cancelled"
    elif order_status == "PROCESSING":
        subject = "Order Confirmation"
    elif order_status == "SHIPPED":
        subject = "Order Shipped"
    elif order_status == "COMPLETED":
        subject = "Order Completed"
    elif order_status == "REFUNDED":
        subject = "Order Initiated"
    
    if not subject:
        return
    
    template_name = subject.lower().replace(" ", "-")
    
    site_name = settings.site_title or settings.WAGTAIL_SITE_NAME or ""
    context = {
        "order": order,
        "site_name": site_name,
        "now": timezone.now(),
        "support_email": settings.contact_emails.splitlines()[0] if settings.contact_emails else "",
        "support_number": settings.contact_numbers.splitlines()[0] if settings.contact_numbers else "",
        "order_detail_url": reverse("my_orders"),
        "retry_payment_url": reverse("razorpay_payment", kwargs={"order_token": order.token}),
    }
    body_text = render_to_string(
        f"emails/{template_name}.txt",
        context=context,
    )
    body_html = render_to_string(
        f"emails/{template_name}.html",
        context=context,
    )
    new_task = ScheduledMessage(
        message_type="email",
        recipient=[order.email],
        subject=subject,
        content=body_text,
        html_content=body_html,
        send_at=timezone.now() + timedelta(seconds=2),
    )
    new_task.save()
    # if debug:
    #     print(body_text)
    #     print()
    #     print()
    #     print()
    #     print()
    #     print()
    #     print(body_html)
    #     return body_html
    # msg = EmailMultiAlternatives(
    #     subject=subject,
    #     body=body_text,
    #     from_email=from_email,
    #     to=["gokulrajendran96@gmail.com"],
    #     # connection=connection,
    # )
    # msg.attach_alternative(body_html, "text/html")
    # return
    # msg.send()


def get_extra_rows(obj):
    extra_rows = {}
    if hasattr(obj, "extra_rows"):
        for identifier, extra_row in obj.extra_rows.items():
            if hasattr(extra_row, 'data'):
                extra_rows[identifier] = extra_row.data
            elif isinstance(extra_row, dict):
                extra_rows[identifier] = extra_row
            else:
                extra_rows[identifier] = str(extra_row)
    return extra_rows


def get_payment_methods(basket, request):
    available_methods = []
    for payment in settings.SALESMAN_PAYMENT_METHODS:
        PaymentMethodClass = import_string(payment)
        payment_instance = PaymentMethodClass()
        if payment_instance.is_available(basket, request):
            available_methods.append(payment_instance)
    return available_methods


def get_full_address(data):
    address_list = []
    full_name = data.get("first_name")
    full_name += f" {data.get('last_name')}" if data.get("last_name") else ""
    company=data.get("company")
    address1=data.get("address1")
    address2=data.get("address2")
    city=data.get("city")
    state=data.get("state")
    country=data.get("country")
    zip=data.get("zip")
    landmark=data.get("landmark")
    phone_number=data.get("phone_number")
    address_list.append(full_name)
    if company:
        address_list.append(company)
    address_list.append(address1)
    if address2:
        address_list.append(address2)
    address_list.append(f"{city} - {zip}")
    address_list.append(f"{state}, {country}")
    address_list.append("Landmark: " + landmark)
    address_list.append("Phone No.: " + phone_number)
    return "\n".join(address_list)
