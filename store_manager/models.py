from django.db import models
from autoslug.fields import AutoSlugField
from wagtail.fields import StreamField
from django.conf import settings
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.models import Orderable, ClusterableModel
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel, ObjectList, TabbedInterface, InlinePanel, MultipleChooserPanel
from collections import defaultdict
import json

from common.blocks import ProductDescriptionBlock
from common.mixins import SEOMixin, SEOExtraMixin, TimestampMixin, ImageMixin
from common.utils import get_placeholder_image


def attribute_value_slug(instance):
    """Generate slug from attribute.name + value"""
    if instance.attribute and instance.value:
        return slugify(f"{instance.attribute.name} {instance.value}")
    return slugify(instance.value or "")


# Create your models here.
class Attribute(ClusterableModel):
    choices = [
        ("default", "Default"),
        ("color", "Color"),
        ("image", "Image"),
    ]
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", blank=True, null=True)
    type = models.CharField(max_length=50, choices=choices, default="default")

    panels = [
        FieldPanel("name"),
        FieldPanel("type"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(panels, heading="Content"),
        ObjectList([InlinePanel("attribute_values")], heading="Values"),
    ])

    def __str__(self):
        return self.name


class AttributeValue(Orderable):
    attribute = ParentalKey("store_manager.Attribute", on_delete=models.CASCADE, related_name="attribute_values", blank=True, null=True)
    value = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=8, blank=True, null=True)
    image = models.ForeignKey("common.MyImage", on_delete=models.SET_NULL, blank=True, null=True, related_name="attribute_images")
    # SEO
    slug = AutoSlugField(populate_from=attribute_value_slug, blank=True, null=True)

    panels = [
        FieldPanel("value"),
        FieldRowPanel([
            FieldPanel("color_code"),
            FieldPanel("image"),
        ])
    ]

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"


class ProductImage(ImageMixin, Orderable):
    product = ParentalKey("store_manager.Product", on_delete=models.CASCADE, related_name="images", blank=True, null=True)
    variation = ParentalKey("store_manager.ProductVariation", on_delete=models.CASCADE, related_name="images", blank=True, null=True)
    panels = ImageMixin.panels

    class Meta(Orderable.Meta):
        pass


class Product(SEOMixin, SEOExtraMixin, TimestampMixin, ClusterableModel):
    categories = ParentalManyToManyField(
        "store_manager.Category",
        related_name="products",
        blank=True,
        help_text=_("Select all relevant categories")
    )
    title = models.CharField(max_length=100, unique=True)
    short_description = StreamField(ProductDescriptionBlock(), blank=True, null=True)
    description = StreamField(ProductDescriptionBlock(), blank=True, null=True)
    specifications = StreamField(ProductDescriptionBlock(), blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_best_selling = models.BooleanField(default=False)
    price_range = models.JSONField(default=dict, blank=True, null=True)

    # ratings
    ratings = models.JSONField(default=dict, blank=True, null=True)

    panels = [
        FieldPanel("categories"),
        FieldPanel("title"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("specifications"),
        MultiFieldPanel([
            MultipleChooserPanel(
                "images",
                label="Product Gallery",
                chooser_field_name="image"
            ),
        ], heading="Gallery"),
    ]
    edit_handler = TabbedInterface([
        ObjectList(panels, heading="Content"),
        ObjectList(SEOMixin.panels + SEOExtraMixin.panels, heading="SEO"),
        ObjectList([InlinePanel("product_variations")], heading="Variations"),
        ObjectList(TimestampMixin.panels, heading="Timestamp"),
    ])

    def x_data(self):
        """{
            selectedSize: null,
            basePrice: 0,
            salePrice: 0,
            prices: {
                small: { base: 20, sale: 18 },
                medium: { base: 25, sale: 22 },
                large: { base: 30, sale: 27 }
            },
            selectSize(size) {
                this.selectedSize = size;
                this.basePrice = this.prices[size].base;
                this.salePrice = this.prices[size].sale;
            }
        }"""
        variations_dict = {}
        for variation in self.product_variations.all():
            variations_dict[variation.id] = {
                "base_price": str(variation.base_price),
                "sale_price": str(variation.sale_price),
            }
        return {
            "price_range": self.price_range,
            "prices": variations_dict
        }
    
    def product_details(self):
        variations = []
        for var in self.product_variations.all():
            variations.append({
                'id': var.id,
                'sku': var.sku,
                'attributes': list(var.attributes.values('id', 'value')),
                'sale_price': str(var.sale_price) if var.sale_price else None,
                'base_price': str(var.base_price) if var.base_price else None,
                'stock': var.stock,
            })
        data = {
            "price_range": self.price_range,
            "variations": variations,
        }
        return json.dumps(data)
        return render(request, 'product.html', {
            'product': product,
            'variations_json': json.dumps(variations)
        })
    
    def product_categories(self):
        categories = set()
        for category in self.categories.all():
            categories.update([c for c in category.breadcrumbs])
        return categories
    
    def product_attributes(self):
        attributes = defaultdict(list)
        for variation in self.product_variations.all():
            attribute_values = variation.attributes.all()
            for value in attribute_values:
                attribute = value.attribute
                if value not in attributes[attribute]:
                    attributes[attribute].append(value)
        return {"keys": attributes.keys(), "attributes": attributes}
    
    @property
    def thumbnail(self):
        images = self.images.all()
        from common.settings import SiteSettings
        common_settings = SiteSettings.load()
        thumb = images[0].image if images else common_settings.placeholder_image
        rendition = thumb.get_rendition("fill-100x100")
        return rendition.url
    
    def __str__(self):
        return self.title


class ProductVariation(TimestampMixin, ClusterableModel, Orderable, models.Model):
    product = ParentalKey("store_manager.Product", on_delete=models.CASCADE, related_name="product_variations")
    sku = models.CharField(_("SKU"), blank=True, null=True, unique=True)
    # image_gallery = ""
    attributes = ParentalManyToManyField("store_manager.AttributeValue")
    # weight and dimensions
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    warranty = models.DecimalField(_("Warranty (years)"), max_digits=3, decimal_places=1, blank=True, null=True)
    base_price = models.DecimalField(_("MRP"), max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("Max. Retail Price"))
    sale_price = models.DecimalField(_("Sale Price"), max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("Sale price. Can be left empty!"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=3, decimal_places=0, default=0)
    stock = models.PositiveBigIntegerField(_("Stock"))
    in_stock = models.BooleanField(blank=True, null=True)
    
    wishlisted_by = ParentalManyToManyField(settings.AUTH_USER_MODEL, related_name="wishlisted_products")

    panels = [
        FieldPanel("sku"),
        MultiFieldPanel([
            FieldPanel("attributes"),
        ], heading="Product Attributes"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("weight"),
                FieldPanel("length"),
                FieldPanel("width"),
                FieldPanel("height"),
            ])
        ], heading="Physical Attributes"),
        MultiFieldPanel([
            FieldPanel("warranty"),
        ]),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("base_price"),
                FieldPanel("sale_price"),
            ]),
        ], heading="Pricing"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("stock"),
                FieldPanel("in_stock"),
            ]),
        ]),
        MultiFieldPanel([
            MultipleChooserPanel(
                "images",
                label="Variation Gallery",
                chooser_field_name="image",
            ),
        ], heading="Gallery"),
    ]

    def get_price(self, request):
        return self.sale_price or self.base_price
    
    @property
    def thumbnail(self):
        images = self.images.all() or self.product.images.all()
        from common.settings import SiteSettings
        common_settings = SiteSettings.load()
        thumb = images[0].image if images else common_settings.placeholder_image
        rendition = thumb.get_rendition("fill-100x100")
        return rendition.url
    
    @property
    def attributes_list(self):
        attrs_list = []
        for attribute in self.attributes.all():
            attrs_list.append({
                "attribute": attribute.attribute.name,
                "value": attribute.value,
            })
        return attrs_list
    
    @property
    def slug(self):
        return self.product.slug

    @property
    def name(self):
        return self.product.title
    
    @property
    def code(self):
        return str(self.id)


class Category(SEOMixin, SEOExtraMixin, TimestampMixin, ClusterableModel):
    title = models.CharField(max_length=255)
    icon = models.ForeignKey("common.MyImage", on_delete=models.SET_NULL, blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,  # Changed from SET_NULL
        null=True, blank=True,
        related_name='children',
        help_text=_("Select a parent category if this is a subcategory")
    )
    
    class Meta:
        unique_together = [['slug', 'parent']]
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    
    panels = [
        FieldPanel("title"),
        FieldPanel("icon"),
        FieldPanel("parent"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(panels, heading="Content"),
        ObjectList(SEOMixin.panels + SEOExtraMixin.panels, heading="SEO"),
        ObjectList(TimestampMixin.panels, heading="Timestamp"),
    ])
    
    @property
    def breadcrumbs(self):
        """Efficient breadcrumb generator"""
        path = []
        current = self
        while current:
            path.append(current)
            current = current.parent
        return reversed(path)
    
    def get_products(self):
        """All products in this category + subcategories"""
        return Product.objects.filter(category__in=self.get_descendants(include_self=True))
    
    def get_descendants(self, include_self=False):
        """Recursive descendants"""
        descendants = [self] if include_self else []
        for child in self.children.all():
            descendants.extend(child.get_descendants(include_self=True))
        return descendants
    
    def __str__(self):
        return f"Category: <{self.title}>"


class Review(TimestampMixin):
    choices = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]
    user = models.ForeignKey("account_manager.User", on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey("store_manager.Product", on_delete=models.CASCADE, blank=True, null=True, related_name="reviews")
    rating = models.IntegerField(choices=choices, default=5)
    title = models.CharField(max_length=255)
    comment = models.TextField()

    class Meta:
        ordering = ("-date_created", "-date_updated")


# django salesman
from salesman.basket.models import BaseBasket, BaseBasketItem
from salesman.orders.models import (
    BaseOrder,
    BaseOrderItem,
    BaseOrderNote,
    BaseOrderPayment,
)


class Basket(BaseBasket):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("Owner"),
        # related_name=""
    )
    pass


class BasketItem(BaseBasketItem):
    pass


class Order(BaseOrder):
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)


class OrderItem(BaseOrderItem):
    pass


class OrderPayment(BaseOrderPayment):
    pass


class OrderNote(BaseOrderNote):
    pass


# pages
from common.mixins import PageBase


def get_min_max_store_price():
    from django.db.models import Min, Max, FloatField
    from django.db.models.fields.json import KeyTextTransform
    from django.db.models.functions import Cast
    min_price = Product.objects.annotate(
        min_price=Cast(KeyTextTransform('min', 'price_range'), FloatField())
    ).aggregate(Min('min_price'))['min_price__min']

    max_price = Product.objects.annotate(
        max_price=Cast(KeyTextTransform('max', 'price_range'), FloatField())
    ).aggregate(Max('max_price'))['max_price__max']
    return {"min": min_price, "max": max_price}


def get_filtered_products(request, products):
    filter_categories = request.GET.getlist("category")
    filter_sizes = request.GET.getlist("size")
    if filter_categories:
        category_ids = []
        for category_slug in filter_categories:
            category_ids.extend([category.id for category in Category.objects.filter(slug=category_slug).first().get_descendants(include_self=True)])
        products = products.filter(categories__in=category_ids)
    if filter_sizes:
        products = products.filter(product_variations__attributes__slug__in=filter_sizes)
    return products


def get_searched_products(request, products):
    query = request.GET.get("q")
    if query:
        query = query.strip()
        products = products.filter(title__icontains=query)
    return products


def get_ordered_products(request, products):
    order_by = request.GET.get("orderby")
    if order_by:
        if order_by == "default" or order_by == "popularity":
            pass
        elif order_by == "rating":
            products = products.order_by("-ratings__avg_rating")
        elif order_by == "date":
            products = products.order_by("-date_created")
        elif order_by == "price":
            products = products.order_by("price_range__min")
        elif order_by == "price-desc":
            products = products.order_by("-price_range__min")
    return products


class ShopPage(PageBase):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        products = Product.objects
        products = get_ordered_products(request, products)
        products = get_filtered_products(request, products)
        products = get_searched_products(request, products)
        context["products"] = products.all()
        context["attributes"] = Attribute.objects.all()
        context["product_filters"] = {
            "pricing": get_min_max_store_price(),
        }
        return context
    
    def serve(self, request, *args, **kwargs):
        # context = self.get_context(request, *args, **kwargs)
        if request.headers.get("HX-Request"):
            self.template = "components/shop_products.html"
        return super().serve(request, *args, **kwargs)


class CheckoutPage(PageBase):
    pass
