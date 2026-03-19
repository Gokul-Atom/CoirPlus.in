from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.models import ClusterableModel, Orderable, Page
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import MultiFieldPanel, FieldPanel, InlinePanel, FieldRowPanel, TabbedInterface, ObjectList
from wagtail.fields import RichTextField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


WEIGHT_UNIT_CHOICES = [
    ("kg", "Kg"),
    ("g", "g"),
]
DIMENSIONS_UNIT_CHOICES = [
    ("mm", "mm"),
    ("cm", "cm"),
    ("in", "in"),
    ("m", "m"),
]


class SocialMediaProfile(Orderable):
    platform = models.CharField(_("Social Media Name"))
    icon_class = models.CharField(_("Icon Class"), blank=True, null=True, help_text=_("Use the Bootstrap Icon class for the social media profile"))
    url = models.URLField(_("Profile Link"), help_text=_("Enter the complete URL of the profile"))
    setting = ParentalKey("common.SiteSettings", on_delete=models.CASCADE, blank=True, null=True, related_name="social_media_profiles")

    panels = [
        FieldRowPanel([
            FieldPanel("platform"),
            FieldPanel("icon_class"),
        ]),
        FieldPanel("url"),
    ]

    def __str__(self):
        return self.platform


class Script(Orderable):
    label = models.CharField(_("Script Label"), max_length=255, help_text=_("This is for admin identification. Use descriptive names for script"))
    Script = models.TextField(_("Script"), help_text=_("Include script tag as well"))
    setting = ParentalKey("common.SiteSettings", on_delete=models.CASCADE, blank=True, null=True, related_name="scripts")

    def __str__(self):
        return self.label


@register_setting
class SiteSettings(BaseGenericSetting, ClusterableModel):
    # General
    site_title = models.CharField(_("Site Title"), max_length=255, default="Site Title")
    tagline = models.CharField(_("Site Description"), max_length=255, default="Tagline goes here...", blank=True, null=True)
    footer_site_title = models.CharField(_("Footer Site Title"), max_length=255, default="Footer Site Title")
    footer_description = RichTextField(_("Footer Description"), blank=True, default="Site Footer Description. Can be left empty!")
    logo = models.ForeignKey("common.MyImage", blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    favicon = models.ForeignKey("common.MyImage", blank=True, null=True, on_delete=models.SET_NULL, related_name="+", help_text=_("Icon to be shown in browser tabs, bookmarks, etc."))
    general_panels = [
        FieldPanel("site_title"),
        FieldPanel("tagline"),
        FieldPanel("footer_site_title"),
        FieldPanel("footer_description"),
        FieldPanel("logo"),
        FieldPanel("favicon"),
    ]

    # Contact Information
    contact_numbers = models.TextField(_("Contact Numbers"), blank=True, null=True, help_text=_("Enter each contact number in separate line"))
    contact_emails = models.TextField(_("Contact Emails"), blank=True, null=True, help_text=_("Enter each contact email in separate line"))
    whatsapp_number = models.CharField(_("WhatsApp Number"), blank=True, null=True, help_text=_("Enter WhatsApp contact number"))
    whatsapp_number_link = models.URLField(_("WhatsApp Number Link"), blank=True, null=True, help_text=_('Enter WhatsApp contact number link. If left empty, "https://wa.me/<whatsapp_number>" will be used'))
    whatsapp_default_message = models.TextField(_("Whatsapp Default Message"), blank=True, null=True, help_text=_("Default message that is pre-filled in whatsapp message"))
    address = models.TextField(_("Address"), blank=True, null=True, help_text=_("Enter the physical address of the business"))
    google_maps_url = models.URLField(_("Google Maps URL"), blank=True, null=True, help_text=_("Paste the URL of the google maps location"))
    google_maps_iframe = models.TextField(_("Google Maps Iframe"), blank=True, null=True, help_text=_("Copy HTML and paste the Embed URL from the google maps"))
    contact_info_panels = [
        MultiFieldPanel([
            FieldPanel("contact_numbers"),
            FieldPanel("contact_emails"),
        ], heading="Contact Details"),
        MultiFieldPanel([
            FieldPanel("whatsapp_number"),
            FieldPanel("whatsapp_number_link"),
            FieldPanel("whatsapp_default_message"),
        ], heading="WhatsApp Details"),
        MultiFieldPanel([
            FieldPanel("address"),
            FieldPanel("google_maps_url"),
            FieldPanel("google_maps_iframe"),
        ], heading="Business Details"),
    ]

    # Social Media Links
    social_media_panels = [
        InlinePanel("social_media_profiles", label="Social Media Profiles"),
    ]

    # Email Settings
    enable_email = models.BooleanField(_("Enable Email?"), default=False, help_text=_("Emails work only if this option is enabled."))
    email_host = models.CharField(_("Email Host"), blank=True, null=True, help_text=_("Eg: mail.mydomain.com, smtp.google.com"))
    email_port = models.IntegerField(_("Email Port"), blank=True, null=True, help_text=_("Eg: 587"))
    use_tls = models.BooleanField(_("Use TLS?"), default=False, help_text=_("Set whether to use TLS"))
    use_ssl = models.BooleanField(_("Use SSL?"), default=False, help_text=_("Set whether to use SSL"))
    email_host_user = models.CharField(_("Email Host User"), blank=True, null=True, help_text=_("Eg: alerts@mydomain.com, info@mydomain.com"))
    email_host_password = models.CharField(_("Email Host Password"), blank=True, null=True, help_text=_("Enter the password of the host user"))
    email_panels = [
        MultiFieldPanel([
            FieldPanel("enable_email"),
        ], heading="Enable / Disable"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel("email_host"),
                FieldPanel("email_port"),
            ]),
            FieldRowPanel([
                FieldPanel("use_tls"),
                FieldPanel("use_ssl"),
            ]),
        ], heading="SMTP Configuration"),
        MultiFieldPanel([
            FieldPanel("email_host_user"),
            FieldPanel("email_host_password"),
        ], heading="Email Account Setup")
    ]

    # Payment Settings
    enable_razorpay = models.BooleanField(_("Enable Razorpay?"), default=False, help_text=_("Enable this to accept test / live payments"))
    test_api_key = models.CharField(_("Test API Key"), blank=True, null=True, help_text=_("Enter the test API Key generated from Razorpay dashboard"))
    test_api_secret = models.CharField(_("Test API Secret"), blank=True, null=True, help_text=_("Enter the test API Secret generated from Razorpay dashboard"))
    enable_live_mode = models.BooleanField(_("Enable Live Mode"), default=False, help_text=_("Enable live mode to accept real payments."))
    live_api_key = models.CharField(_("Live API Key"), blank=True, null=True, help_text=_("Enter the live API Key generated from Razorpay dashboard"))
    live_api_secret = models.CharField(_("Live API Secret"), blank=True, null=True, help_text=_("Enter the live API Secret generated from Razorpay dashboard"))
    payment_panels = [
        MultiFieldPanel([
            FieldPanel("enable_razorpay"),
        ], heading="Enable / Disable"),
        MultiFieldPanel([
            FieldPanel("test_api_key"),
            FieldPanel("test_api_secret"),
        ], heading="Test API Configuration"),
        MultiFieldPanel([
            FieldPanel("enable_live_mode"),
            FieldPanel("live_api_key"),
            FieldPanel("live_api_secret"),
        ], heading="Live API Configuration"),
    ]

    # Tax Rates
    enable_tax_rates = models.BooleanField(_("Enable Tax Rates?"), default=False, help_text=_("Enable tax rates calculation before checkout"))
    cgst_tax_percent = models.DecimalField(_("CGST Tax %"), blank=True, null=True, max_digits=5, decimal_places=2, help_text=_("Enter the CSGT tax percentage"))
    sgst_tax_percent = models.DecimalField(_("SGST Tax %"), blank=True, null=True, max_digits=5, decimal_places=2, help_text=_("Enter the SSGT tax percentage"))
    igst_tax_percent = models.DecimalField(_("IGST Tax %"), blank=True, null=True, max_digits=5, decimal_places=2, help_text=_("Enter the ISGT tax percentage"))
    # principal_state_gst = models.ForeignKey("service_manager.State", blank=True, null=True, on_delete=models.SET_NULL, related_name="+", help_text=_("Select the Principal State of Business"))
    tax_panels = [
        MultiFieldPanel([
            FieldPanel("enable_tax_rates"),
        ], heading="Enable / Disable"),
        MultiFieldPanel([
            FieldPanel("cgst_tax_percent"),
            FieldPanel("sgst_tax_percent"),
            FieldPanel("igst_tax_percent"),
        ], heading="Tax Rates %"),
        MultiFieldPanel([
            # FieldPanel("principal_state_gst"),
        ], heading="Business Location"),
    ]

    # Store Settings
    weight_unit = models.CharField(_("Weight (unit)"), default="kg", choices=WEIGHT_UNIT_CHOICES)
    dimensions_unit = models.CharField(_("Dimensions (unit)"), default="cm", choices=DIMENSIONS_UNIT_CHOICES)
    track_stock = models.BooleanField(_("Track stock?"), default=False)

    store_settings_panels = [
        FieldPanel("weight_unit"),
        FieldPanel("dimensions_unit"),
        FieldPanel("track_stock"),
    ]

    # Page Settings
    home_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    shop_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    cart_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    wishlist_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    account_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    checkout_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    contact_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    blog_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    about_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")
    privacy_policy_page = models.ForeignKey(Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="+")

    page_settings_panels = [
        FieldPanel("home_page"),
        FieldPanel("shop_page"),
        FieldPanel("cart_page"),
        FieldPanel("wishlist_page"),
        FieldPanel("account_page"),
        FieldPanel("checkout_page"),
        FieldPanel("contact_page"),
        FieldPanel("blog_page"),
        FieldPanel("about_page"),
        FieldPanel("privacy_policy_page"),
    ]

    # SEO
    add_site_title_to_meta_title = models.BooleanField(_("Add Site title to Meta title"), default=True, help_text=_("Set whether to add site title to meta title"))
    add_spaces = models.BooleanField(_("Add Spaces"), default=True, help_text=("Set whether to add spaces around the separator. Takes 2 character spaces"))
    separator = models.CharField(_("Separator"), default="|", max_length=1, help_text=_("Eg: |, -"))
    meta_title_length = models.PositiveIntegerField(_("Meta Title Length"), default=60, help_text=_("Length of the meta title including meta title or title, spaces, separator, site_title. Extra characters will be truncated"))
    meta_description_length = models.PositiveIntegerField(_("Meta Description Length"), default=160, help_text=_("Length of the meta description. Extra characters will be truncated"))
    placeholder_image = models.ForeignKey("common.MyImage", blank=True, null=True, on_delete=models.SET_NULL, related_name="+", help_text=_("This image will be used if there is no image"))

    seo_panels = [
        MultiFieldPanel([
            FieldPanel("add_site_title_to_meta_title"),
            FieldPanel("add_spaces"),
            FieldPanel("separator"),
            FieldPanel("meta_title_length"),
            FieldPanel("meta_description_length"),
        ], heading="Basics"),
        MultiFieldPanel([
            FieldPanel("placeholder_image"),
        ], heading="Others"),
        MultiFieldPanel([
            InlinePanel("scripts"),
        ], heading="Scripts"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(general_panels, heading="General"),
        ObjectList(contact_info_panels, heading="Contact Information"),
        ObjectList(social_media_panels, heading="Social Media Profiles"),
        ObjectList(email_panels, heading="Email Settings"),
        ObjectList(payment_panels, heading="Payment Settings"),
        ObjectList(tax_panels, heading="Tax Rates"),
        ObjectList(store_settings_panels, heading="Store Settings"),
        ObjectList(page_settings_panels, heading="Page Settings"),
        ObjectList(seo_panels, heading="SEO"),
    ])

    def clean(self):
        super().clean()
        errors = {}
        if self.enable_email:
            if not self.email_host:
                errors.update({"email_host": "This field is required for sending email notifications"})
            if not self.email_port:
                errors.update({"email_port": "This field is required for sending email notifications"})
            if not self.email_host_user:
                errors.update({"email_host_user": "This field is required for sending email notifications"})
            if not self.email_host_password:
                errors.update({"email_host_password": "This field is required for sending email notifications"})
        if self.enable_razorpay:
            if not self.test_api_key:
                errors.update({"test_api_key": "This is required for accepting test payments."})
            if not self.test_api_secret:
                errors.update({"test_api_secret": "This is required for accepting test payments."})
        if self.enable_live_mode:
            if not self.enable_razorpay:
                errors.update({"enable_razorpay": "This should be enabled first before enabling live mode."})
                errors.update({"enable_live_mode": "Enable Razorpay before enabling this."})
            if not self.live_api_key:
                errors.update({"live_api_key": "This is required for accepting live payments."})
            if not self.live_api_secret:
                errors.update({"live_api_secret": "This is required for accepting live payments."})
        if self.enable_tax_rates:
            # if not self.principal_state_gst:
            #     errors.update({"principal_state_gst": "Prinicipal State of Business is required for tax calculation! Disable tax rates to leave this empty!"})
            if not self.cgst_tax_percent:
                errors.update({"cgst_tax_percent": "This should be a valid percent for tax calculation"})
            if not self.sgst_tax_percent:
                errors.update({"sgst_tax_percent": "This should be a valid percent for tax calculation"})
            if not self.igst_tax_percent:
                errors.update({"igst_tax_percent": "This should be a valid percent for tax calculation"})
        if not self.placeholder_image:
            errors.update({"placeholder_image": "Select the Placeholder Image that is to be used if the image is not selected"})
        if errors:
            raise ValidationError(errors)
