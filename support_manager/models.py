from django.db import models
from common.mixins import PageBase, SEOExtraMixin, TimestampMixin
from django.template.response import TemplateResponse
from account_manager.models import RecentlyViewed


# Create your models here.
class Contact(TimestampMixin, models.Model):
    full_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.full_name


# pages
class SinglePolicyPage(PageBase, SEOExtraMixin):
    pass


class ContactPage(PageBase, SEOExtraMixin):
    def get_context(self, request, *args, **kwargs):
        from .forms import ContactForm
        context = super().get_context(request, *args, **kwargs)
        context["contact_form"] = ContactForm()
        if request.user.is_authenticated:
            recently_viewed = RecentlyViewed.objects.filter(user=request.user)
        else:
            recently_viewed = RecentlyViewed.objects.filter(session_id=request.session.session_key)
        context["recently_viewed"] = recently_viewed
        return context
    
    def serve(self, request, *args, **kwargs):
        from .forms import ContactForm
        context = self.get_context(request, *args, **kwargs)
        if request.method == "POST":
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                contact_form.save()
                if request.headers.get("HX-Request"):
                    return TemplateResponse(request, "components/contact_form_landing.html", context={})
            else:
                context["contact_form"] = contact_form
                return TemplateResponse(request, "components/contact_form.html", context=context)
        return super().serve(request, *args, **kwargs)
