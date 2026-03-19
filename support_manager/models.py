from django.db import models
from common.mixins import PageBase, SEOExtraMixin, TimestampMixin


# Create your models here.
class Contact(TimestampMixin, models.Model):
    full_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message = models.TextField()


# pages
class SinglePolicyPage(PageBase, SEOExtraMixin):
    pass


class ContactPage(PageBase, SEOExtraMixin):
    pass
