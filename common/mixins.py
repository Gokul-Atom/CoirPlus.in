from django.db import models
from wagtail.models import Page
from wagtail.admin.forms import WagtailAdminPageForm
from django.utils.translation import gettext_lazy as _
from autoslug import AutoSlugField
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError
from wagtail.admin.panels import MultiFieldPanel, FieldPanel, ObjectList, TabbedInterface, HelpPanel, InlinePanel
from wagtail.fields import StreamField, StreamBlock
from modelcluster.tags import ClusterTaggableManager
from .blocks import CustomBlock, ProductDescriptionBlock


class SEOMixin(models.Model):
    slug = AutoSlugField(max_length=255, populate_from="title", blank=True, editable=True)
    seo_title = models.TextField(max_length=60, blank=True, null=True)
    search_description = models.TextField(max_length=160, blank=True, null=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("slug"),
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
        ], heading="For Search Engines")
    ]

    class Meta:
        abstract = True


class SEOExtraMixin(models.Model):
    meta_image = models.ForeignKey("common.MyImage", on_delete=models.SET_NULL, blank=True, null=True, related_name="+", help_text=_("This image will appear when the page is shared"))
    canonical_url = models.CharField(_("Canonical URL"), blank=True, help_text=_("If this is the duplicate page and paste the URL of the original page"))
    schema_markup = models.TextField(_("Schema Markup"), blank=True, help_text=_("Include the script tag as well. SEO Purposes Only!"))

    panels = [
        MultiFieldPanel([
            FieldPanel("meta_image"),
            FieldPanel("canonical_url"),
            FieldPanel("schema_markup"),
        ], heading="Extras"),
    ]

    class Meta:
        abstract = True


class ImageMixin(models.Model):
    image = models.ForeignKey("common.MyImage", on_delete=models.SET_NULL, blank=True, null=True, related_name="+")
    
    class Meta:
        abstract=True
    
    panels = [
        FieldPanel("image", classname="w-md-50"),
    ]


class TimestampMixin(models.Model):
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True)

    panels = [
        MultiFieldPanel([
            HelpPanel(template="panels/timestamp_panel.html"),
        ], heading="Timestamp"),
    ]

    class Meta:
        abstract = True


class ContentBasePage(Page, SEOExtraMixin, TimestampMixin):
    body = StreamField(CustomBlock(), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
    promote_panels = Page.promote_panels + SEOExtraMixin.panels
    timestamp_panels = TimestampMixin.panels
    settings_panels = Page.settings_panels
    
    class Meta:
        abstract = True
    
    def clean(self):
        super().clean()
        errors = getattr(self, '_errors', {})
        if self.seo_title:
            try:
                MaxLengthValidator(60)(self.seo_title)
            except ValidationError:
                errors['seo_title'] = ["SEO title should be <= 60 characters"]
        if self.search_description:
            try:
                MaxLengthValidator(160)(self.search_description)
            except ValidationError:
                errors['search_description'] = ["Meta description should be <= 160 characters"]
        if errors:
            self._errors = errors
            raise ValidationError(errors)


class PageBase(ContentBasePage):
    content_panels = ContentBasePage.content_panels
    promote_panels = ContentBasePage.promote_panels
    timestamp_panels = ContentBasePage.timestamp_panels
    settings_panels = ContentBasePage.settings_panels

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Content"),
        ObjectList(promote_panels, heading="Promote"),
        ObjectList(timestamp_panels, heading="Timestamp"),
        ObjectList(settings_panels, heading="Settings"),
    ])

    class Meta:
        abstract = True


# class ServiceProductPageBase(ContentBasePage):
#     faqs = StreamField([
#         ("faq_block", FAQBlock()),
#         ], blank=True)
#     tags = ClusterTaggableManager(blank=True, through="service_manager.ServiceProductTag", verbose_name="Service Tags")
#     documents_required_title = models.CharField(_("Title"), blank=True, help_text=_('Title to put above the required documents. Prefixed with "Documents Required For"'))
#     service_form_intro = StreamField(CustomBlock(), blank=True, null=True)
#     service_form = models.ForeignKey(
#         "service_manager.ServiceProductForm",
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         related_name="service_product",
#     )
    
#     content_panels = ContentBasePage.content_panels + [
#         FieldPanel("faqs"),
#         FieldPanel("tags"),
#     ]
#     documents_panels = [
#         FieldPanel("documents_required_title"),
#         InlinePanel("service_documents", label="Documents"),
#     ]
#     service_form_panels = [
#         FieldPanel("service_form_intro"),
#         FieldPanel("service_form"),
#     ]
#     promote_panels = ContentBasePage.promote_panels
#     timestamp_panels = ContentBasePage.timestamp_panels
#     settings_panels = ContentBasePage.settings_panels

#     edit_handler = TabbedInterface([
#         ObjectList(content_panels, heading="Content"),
#         ObjectList(documents_panels, heading="Documents Required"),
#         ObjectList(service_form_panels, heading="Service Form"),
#         ObjectList(promote_panels, heading="Promote"),
#         ObjectList(timestamp_panels, heading="Timestamp"),
#         ObjectList(settings_panels, heading="Settings"),
#     ])

#     class Meta:
#         abstract = True


class BlogPostBase(ContentBasePage):
    featured_image = models.ForeignKey("common.MyImage", blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    views = models.PositiveBigIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=1)

    content_panels = ContentBasePage.content_panels + [
        FieldPanel("featured_image"),
    ]
    promote_panels = ContentBasePage.promote_panels
    timestamp_panels = ContentBasePage.timestamp_panels
    settings_panels = ContentBasePage.settings_panels

    class Meta:
        abstract = True
