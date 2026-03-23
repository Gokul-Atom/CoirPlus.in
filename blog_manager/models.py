from django.db import models
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList

from common.mixins import PageBase


# Create your models here.
class BlogIndexPage(PageBase):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        blog_query = request.GET.get("blog")
        if  blog_query:
            context["posts"] = self.get_children().live().public().search(blog_query)
        else:
            context["posts"] = self.get_children().live().public()
        return context


class PostPage(PageBase):
    featured_image = models.ForeignKey("common.MyImage", on_delete=models.SET_NULL, blank=True, null=True, related_name="+")
    views = models.PositiveBigIntegerField(default=0)

    content_panels = PageBase.content_panels + [
        FieldPanel("featured_image"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Content"),
        ObjectList(PageBase.promote_panels, heading="Promote"),
        ObjectList(PageBase.timestamp_panels, heading="Timestamp"),
        ObjectList(PageBase.settings_panels, heading="Settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related_posts"] = self.get_siblings(inclusive=False)
        return context
