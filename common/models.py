from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from django.utils.translation import gettext_lazy as _
from .mixins import PageBase


# Create your models here.
class MyImage(AbstractImage):
    alt_text = models.CharField(_("Alt text"), max_length=255, blank=True, null=True, help_text=_("Alternative text for accessibility; describe what is in the image."))
    caption = models.CharField(_("Caption"), max_length=255, blank=True, null=True, help_text=_("Caption text; will be shown below the image."))
    admin_form_fields = Image.admin_form_fields + ("alt_text", "caption")

    @property
    def default_alt_text(self):
        return self.alt_text or ""
    
    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")


class ImageRendition(AbstractRendition):
    image = models.ForeignKey("common.MyImage", on_delete=models.CASCADE, related_name="renditions")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["image", "filter_spec", "focal_point_key"],
                name="unique_rendition",
            )
        ]


class ScheduledMessage(models.Model):
    to_emails = models.TextField(help_text="Comma-separated list of recipient emails")
    subject = models.CharField(max_length=255)
    text_body = models.TextField(blank=True, null=True)
    html_body = models.TextField(blank=True, null=True)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject} -> {self.to_emails}"


# pages
class SimplePage(PageBase):
    pass


from .settings import SiteSettings
