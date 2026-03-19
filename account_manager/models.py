from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django.utils import timezone

from common.mixins import PageBase, SEOExtraMixin, TimestampMixin


# Pages
class MyAccountPage(PageBase):
    pass


class WishlistPage(PageBase):
    pass


class CartPage(PageBase):
    pass


# Create your models here.
class User(AbstractUser):
    pass
    # phone_regex = RegexValidator(
    #     regex=r"^\+?1?\d{9,15}$",
    #     message=_("Phone number must be entered in the format: '+919XXXXXXXXX'. Up to 15 digits allowed")
    # )
    # phone_number = models.CharField(
    #     verbose_name=_("Phone Number"),
    #     validators=[phone_regex],
    #     max_length=17,
    #     blank=True,
    #     null=True,
    #     help_text=_("Contact phone number"),
    # )
    # profile_picture = models.ForeignKey(
    #     "common.MyImage",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    #     verbose_name=_("Profile picture"),
    #     related_name="+",
    # )
    # default_delivery_address = models.ForeignKey(
    #     "account_manager.address",
    #     on_delete=models.SET_NULL,
    #     blank=True,
    #     null=True,
    #     verbose_name=_("Default delivery address"),
    #     related_name="+",
    # )
    # @property
    # def display_name(self):
    #     return self.first_name if self.first_name else self.username
    
    # def __str__(self):
    #     return self.get_full_name() or self.username


class CheckoutAddress(models.Model):
    # phone_regex = RegexValidator(
    #     regex=r"^\+?1?\d{9,15}$",
    #     message=_("Phone number must be entered in the format (country code + phone number): '919XXXXXXXXX'. Up to 15 digits allowed")
    # )
    # zip_regex = RegexValidator(
    #     regex=r"^\d{6,8}$",
    #     message=_("Enter a valid zip/postal code. Can be 6-8 digits long.")
    # )
    user = models.ForeignKey("account_manager.User", on_delete=models.CASCADE, related_name="addresses", verbose_name=_("User"))
    first_name = models.CharField(_("First name"), max_length=255, blank=True, null=True)
    last_name = models.CharField(_("Last name"), max_length=255, blank=True, null=True)
    email = models.EmailField(_("Email Address"), max_length=255, blank=True, null=True)
    company = models.CharField(_("Company"), max_length=255, blank=True, null=True)
    address1 = models.CharField(_("Address line 1"), max_length=255, blank=True, null=True)
    address2 = models.CharField(_("Address line 2"), max_length=255, blank=True, null=True)
    city = models.CharField(_("City"), max_length=255, blank=True, null=True)
    state = models.CharField(_("State"), max_length=255, blank=True, null=True)
    # country = models.CharField(_("Country"), max_length=255)  # Consider django-countries package
    country = CountryField(_("Country"), blank=True, null=True)
    zip = models.CharField(_("Postcode/Zip"), max_length=20, blank=True, null=True)
    landmark = models.CharField(_("Landmark"), max_length=255, blank=True, null=True)
    phone_number = models.CharField(_("Phone number"), max_length=20, blank=True, null=True)
    is_billing = models.BooleanField(
        _("Billing address"),
        default=False,
        help_text=_("Use as billing address"),
        blank=True,
    )
    is_shipping = models.BooleanField(
        _("Shipping address"),
        default=False,
        help_text=_("Use as shipping address"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ['user', 'is_shipping', 'is_billing']
    
    @property
    def full_name(self):
        full_name = self.first_name
        full_name += " " + self.last_name if self.last_name else ""
        return full_name
    
    @property
    def full_address(self):
        address = self.address1
        address += ", " + self.address2 if self.address2 else ""
        return address
    
    def display_address(self):
        temp = f"<strong>{self.full_name}</strong>"
        temp += ",<br> " + self.company if self.company else ""
        temp += f"<br>{self.full_address}, {self.city} - {self.zip}, {self.state}, {self.country.name}"
        temp += f"<br><strong>Landmark:</strong> {self.landmark}" if self.landmark else ""
        temp += f"<br><strong>Phone No.:</strong> {self.phone_number}"
        return temp
    
    def plain_address(self):
        temp = f"{self.full_name}"
        temp += ", " + self.company if self.company else ""
        temp += f"{self.full_address}, {self.city} - {self.zip}, {self.state}, {self.country.name} | "
        temp += f"Landmark: {self.landmark} | " if self.landmark else ""
        temp += f"Phone No.: {self.phone_number}"
        return temp

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# class RecentlyViewed(TimestampMixin, models.Model):
#     pass
    # user = models.ForeignKey("account_manager.User", on_delete=models.CASCADE, related_name="recently_viewed_items")
    # product = models.ForeignKey("store_manager.Product", on_delete=models.CASCADE, related_name="recently_viewed_by_users")

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=["user", "product"], name="unique_recently_viewed")
    #     ]
    #     ordering = ("-updated_at",)

    # def __str__(self):
    #     return f"{self.user.display_name} viewed {self.product} at {self.updated_at}"


# class Invoice(models.Model):
#     pass
    # order = models.OneToOneField("checkout_manager.Order", on_delete=models.CASCADE, related_name="invoice")
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    # invoice_number = models.CharField(max_length=100, blank=True, unique=True, editable=False)
    # created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     if not self.invoice_number:
    #         current_year = timezone.now().year
    #         with transaction.atomic():
    #             last_invoice = Invoice.objects.select_for_update().filter(created_at__year=current_year).order_by("id").last()
    #             if last_invoice:
    #                 last_no = int(last_invoice.invoice_number.split("-")[-1])
    #                 new_no = last_no + 1
    #             else:
    #                 new_no = 1
    #             # Invoice format
    #             self.invoice_number = f"INV-{current_year}-{new_no:05d}"
    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"Invoice {self.invoice_number} for Order {self.order.ref}"
