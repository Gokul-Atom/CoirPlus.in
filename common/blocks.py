from wagtail import blocks
from wagtail.models import Page
from wagtail.images.blocks import ImageChooserBlock
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.apps import apps
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock
from wagtail.snippets.blocks import SnippetChooserBlock
import json


FAQ_CHOICES = (
    ("general", "General"),
    ("service", "Service"),
)


class CSSBase(blocks.StructBlock):
    css_id = blocks.RegexBlock(
        regex=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
        required=False,
        help_text=_("CSS ID"),
        error_messages={
            "invalid": "Invalid CSS ID format"
        }
    )
    css_class = blocks.RegexBlock(
        regex=r"^[a-zA-Z][a-zA-Z0-9_-]*(\s+[a-zA-Z][a-zA-Z0-9_-]*)*$",
        required=False,
        help_text=_("CSS Class name"),
        error_messages={
            "invalid": "Invalid CSS Class format"
        }
    )
    css_style = blocks.TextBlock(
        required=False,
        help_text=_("Enter the CSS Style for this block"),
    )


class SplideBase(CSSBase):
    options = """{
        type: "loop",
        autoplay: true,
        interval: 3000,
    }"""
    splide_id = blocks.RegexBlock(
        regex=r"^[a-zA-Z][a-zA-Z0-9_-]*$",
        required=False,
        help_text=_("CSS ID"),
        error_messages={
            "invalid": "Invalid Splide ID format"
        }
    )
    splide_options = blocks.TextBlock(required=False, default=options, help_text=f"Configure banner options as JSON, e.g. {options}")


class AdvancedRichText(CSSBase):
    rich_text = blocks.RichTextBlock()

    class Meta:
        template = "blocks/advanced_rich_text.html"


class BlocksBase(blocks.StreamBlock):
    rich_text = blocks.RichTextBlock(required=False)
    advanced_rich_text = AdvancedRichText(required=False)
    html = blocks.RawHTMLBlock(label="HTML")


class ImageBannerItem(blocks.StructBlock):
    image = ImageChooserBlock()
    link = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)


class ImageBanner(SplideBase):
    label = blocks.CharBlock(max_length=50)
    slides = blocks.ListBlock(ImageBannerItem())


class ImageBlock(CSSBase):
    small_screen_image = ImageChooserBlock(required=False)
    large_screen_image = ImageChooserBlock(required=False)
    link = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)

    class Meta:
        template = "blocks/image_block.html"


class SimpleImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    link = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)


class TwoColumnImageBlock(CSSBase):
    images = blocks.ListBlock(SimpleImageBlock(), max_num=2)

    class Meta:
        template = "blocks/two_column_image_block.html"


class HomeHeroSection(blocks.StructBlock):
    banner1 = ImageBanner()
    banner2 = ImageBanner()
    banner3 = ImageBanner()

    class Meta:
        template = "blocks/home_hero_section.html"


class FeaturedProductsSection(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)

    def get_context(self, value, parent_context=None):
        from store_manager.models import Product
        context = super().get_context(value, parent_context)
        context["products"] = Product.objects.filter(is_featured=True).all()
        return context

    class Meta:
        template = "blocks/featured_products_section.html"


class BestSellingProductsSection(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)

    def get_context(self, value, parent_context=None):
        from store_manager.models import Product
        context = super().get_context(value, parent_context)
        context["products"] = Product.objects.filter(is_best_selling=True).all()
        return context

    class Meta:
        template = "blocks/best_selling_products_section.html"


class IconCardItem(blocks.StructBlock):
    icon = ImageChooserBlock()
    title = blocks.CharBlock()
    description = BlocksBase()


class IconCards(CSSBase):
    cards = blocks.ListBlock(IconCardItem())

    class Meta:
        template = "blocks/icon_cards.html"


class MaterialCardItem(blocks.StructBlock):
    image = ImageChooserBlock()
    title = blocks.CharBlock()
    description = BlocksBase()
    link = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)


class MaterialCards(CSSBase):
    heading = blocks.CharBlock()
    cards = blocks.ListBlock(MaterialCardItem())

    class Meta:
        template = "blocks/material_section.html"


class MattressBenefitItem(blocks.StructBlock):
    image = ImageChooserBlock()
    title = blocks.CharBlock()
    description = BlocksBase()


class MattressBenefitsSection(CSSBase):
    heading = blocks.CharBlock()
    main_image = ImageChooserBlock()
    cards_group_1 = blocks.ListBlock(MattressBenefitItem(), max_num=3)
    cards_group_2 = blocks.ListBlock(MattressBenefitItem(), max_num=3)

    class Meta:
        template = "blocks/mattress_benefits_section.html"


class MattressSizeItem(blocks.StructBlock):
    image = ImageChooserBlock()
    title = blocks.CharBlock()
    description = BlocksBase()
    link = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)


class MattressSizeSection(CSSBase):
    heading = blocks.CharBlock()
    cards = blocks.ListBlock(MattressSizeItem())

    class Meta:
        template = "blocks/mattress_size_section.html"


class CTABlock(CSSBase):
    background_image = ImageChooserBlock()
    cta_title = blocks.CharBlock()
    cta_text = blocks.CharBlock()
    icon = blocks.CharBlock(required=False)
    link = blocks.CharBlock(required=False)
    page = blocks.PageChooserBlock(required=False)

    class Meta:
        template = "blocks/cta_section.html"


class ProductDescriptionGallery(CSSBase):
    images = blocks.ListBlock(ImageBannerItem())

    class Meta:
        template = "blocks/product_gallery.html"

# class TitleBlock(StructBlockBase):
#     title = blocks.CharBlock(
#         help_text=_("Use this block for page title (H1 tag)")
#     )

#     class Meta:
#         template = "blocks/title_block.html"
#         form_classname = "title-block"


# class SectionTitleBlock(StructBlockBase):
#     title = blocks.CharBlock(
#         help_text=_("Use this block for page title (H2 tag)")
#     )

#     class Meta:
#         template = "blocks/section_title_block.html"
#         form_classname = "section-title-block"


# class IconCardItem(blocks.StructBlock):
#     icon = blocks.RegexBlock(
#         regex=r"^[a-zA-Z][a-zA-Z0-9_-]*(\s+[a-zA-Z][a-zA-Z0-9_-]*)*$",
#         required=False,
#         help_text=_("Icon class name Eg: bi-star, bi-shield-tick"),
#         error_messages={
#             "invalid": "Invalid Icon class format"
#         }
#     )
#     icon_image = ImageChooserBlock(
#         required=False,
#         help_text=_("This is ignored when the icon is not empty")
#     )
#     title = blocks.CharBlock(
#         help_text=_("Title of this card")
#     )
#     content = blocks.TextBlock(
#         help_text=_("Content of this card")
#     )

#     class Meta:
#         form_classname = "icon-card"


# class SpacerBlock(blocks.StructBlock):
#     mobile = blocks.IntegerBlock(
#         required=False,
#     )
#     tablet = blocks.IntegerBlock(
#         required=False,
#     )
#     desktop = blocks.IntegerBlock(
#         required=False,
#     )

#     def clean(self, value):
#         result = super().clean(value)
#         if not (result.get("mobile") or result.get("tablet") or result.get("desktop")):
#             raise ValidationError(_("Atleast one of mobile, tablet or desktop spacing must be set"))
#         return result
    
#     class Meta:
#         template = "blocks/spacer_block.html"
#         form_classname = "spacer"
#         icon = "grip"


# class IconCardsBlock(StructBlockBase):
#     cards = blocks.ListBlock(IconCardItem())

#     class Meta:
#         template = "blocks/icon_cards_block.html"


# # class BadgeTextBlock(StructBlockBase):
# #     title = blocks.CharBlock()
# #     badge_style = blocks.ChoiceBlock(
# #         choices=BADGE_TEXT_CHOICES,
# #         default=1
# #     )

# #     class Meta:
# #         template = "blocks/badge_text_block.html"


# class ServiceCardsBlock(StructBlockBase):
#     pass


class FAQItem(blocks.StructBlock):
    question = blocks.TextBlock()
    answer = blocks.RichTextBlock(features=["bold", "italic", "ol", "ul", "link"])


class FAQBlock(CSSBase):
    heading = blocks.CharBlock(required=False)
    body = BlocksBase(required=False)
    items = blocks.ListBlock(
        FAQItem()
    )

    class Meta:
        template = "blocks/faq_section.html"


# class TableBlock(TypedTableBlock):
#     text = blocks.CharBlock(required=False)
#     rich_text = blocks.RichTextBlock(required=False, features=["bold", "italic", "ol", "ul", "link"])

#     class Meta:
#         template = "blocks/table_block.html"


# ## Sections
# # class CTABlock(blocks.StructBlock):
# #     cta_button_text = blocks.CharBlock(label="CTA Text")
# #     cta_open_in_new = blocks.BooleanBlock(
# #         required=False,
# #         help_text=_("Open in New tab?")
# #         )
# #     cta_button_link_page = blocks.PageChooserBlock(label="CTA Page", required=False)
# #     cta_button_link_url = blocks.CharBlock(label="CTA URL", required=False)
# #     cta_button_type = blocks.ChoiceBlock(
# #         choices=BUTTON_CHOICES,
# #         default=1,
# #         help_text=_('Select the button type. Note: Button Type "4" is a submit button')
# #     )


# class HeroSectionBlock(blocks.StructBlock):
#     title = blocks.CharBlock()
#     subtitle = blocks.CharBlock()
#     body = blocks.StreamBlock([
#         ("rich_text", blocks.RichTextBlock()),
#     ], required=False)
#     cta_button_link_page = blocks.PageChooserBlock(required=False, label="CTA Page")
#     cta_button_link_url = blocks.CharBlock(required=False, label="CTA URL")
#     cta_button_text = blocks.CharBlock(label="CTA Text")
#     background_image = ImageChooserBlock(label="Background Image")

#     class Meta:
#         template = "blocks/hero_section_block.html"


# class HeroSectionGeneral(StructBlockBase):
#     title = blocks.CharBlock()
#     subtitle = blocks.CharBlock(required=False)
#     body = blocks.StreamBlock([
#         ("rich_text", blocks.RichTextBlock()),
#     ], required=False)
#     # ctas = blocks.ListBlock(CTABlock())
#     background_image = ImageChooserBlock(label="Background Image", required=False)
#     background_image_mobile = ImageChooserBlock(label="Background Image (Mobile)", required=False)

#     class Meta:
#         template = "blocks/hero_section_general_block.html"


# class SmallAboutBlock(blocks.StructBlock):
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     cta_button_link_page = blocks.PageChooserBlock(required=False, label="CTA Page")
#     cta_button_link_url = blocks.CharBlock(required=False, label="CTA URL")
#     cta_button_text = blocks.CharBlock(label="CTA Text", required=False)
#     icon_cards =  blocks.ListBlock(IconCardItem(), form_classname="icon-cards")
#     section_image = ImageChooserBlock(label="Section Image")

#     class Meta:
#         template = "blocks/small_about_section_block.html"


# class FeaturedServices(blocks.StructBlock):
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     # badges = blocks.ListBlock(BadgeTextBlock())

#     def get_context(self, value, parent_context=None):
#         context = super().get_context(value, parent_context)
#         SeriveCategoryPage = apps.get_model(
#             app_label="service_manager",
#             model_name="servicecategorypage",
#         )
#         ServiceCategoryPages = SeriveCategoryPage.objects.live().filter(is_featured=True)
#         context["services"] = ServiceCategoryPages
#         return context

#     class Meta:
#         template = "blocks/featured_services.html"


# class AllServices(blocks.StructBlock):
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     limit = blocks.IntegerBlock(required=False)
#     badges = blocks.ListBlock(BadgeTextBlock())

#     def get_context(self, value, parent_context=None):
#         context = super().get_context(value, parent_context)
#         ServiceCategoryPage = apps.get_model(
#             app_label="service_manager",
#             model_name="servicecategorypage",
#         )
#         all_services = ServiceCategoryPage.objects.live()
#         limit = value.get("limit")
#         if limit and limit > 0:
#             all_services = all_services[:limit]
#         context["all_services"] = all_services
#         return context
    
#     class Meta:
#         template = "blocks/all_services.html"


# class StepCard(blocks.StructBlock):
#     icon = ImageChooserBlock()
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock()


# class FilingSteps(blocks.StructBlock):
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     badges = blocks.ListBlock(BadgeTextBlock())
#     steps = blocks.ListBlock(StepCard())

#     class Meta:
#         template = "blocks/filing_steps.html"


# class ClientLogoBlock(blocks.StructBlock):
#     logo = ImageChooserBlock()
#     name = blocks.CharBlock(required=False)


# class ClientSectionBlock(SplideMixin, blocks.StructBlock):
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     badges = blocks.ListBlock(BadgeTextBlock())
#     clients = blocks.ListBlock(ClientLogoBlock())

#     class Meta:
#         template = "blocks/client_section_block.html"


# class OurServicesSmallBlock(StructBlockBase):
#     image = ImageChooserBlock()
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     badges = blocks.ListBlock(BadgeTextBlock())

#     class Meta:
#         template = "blocks/our_services_small_block.html"


# class BenefitsSectionBlock(StructBlockBase):
#     title = blocks.CharBlock()
#     subtitle = blocks.CharBlock(required=False)
#     body = blocks.RichTextBlock(required=False)
#     cta_button_link_page = blocks.PageChooserBlock(required=False, label="CTA Page")
#     cta_button_link_url = blocks.CharBlock(required=False, label="CTA URL")
#     cta_button_text = blocks.CharBlock(label="CTA Text", required=False)
#     badges = blocks.ListBlock(BadgeTextBlock())
#     benefit_cards =  blocks.ListBlock(IconCardItem(), form_classname="icon-cards")

#     class Meta:
#         template = "blocks/benefits_section_block.html"


# class TestimonialItem(blocks.StructBlock):
#     title = blocks.CharBlock()
#     comment = blocks.RichTextBlock()
#     name = blocks.CharBlock()
#     designation = blocks.CharBlock()
#     profile = ImageChooserBlock()


# class TestimonialSectionBlock(StructBlockBase, SplideMixin):
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     badges = blocks.ListBlock(BadgeTextBlock())
#     testimonials = blocks.ListBlock(TestimonialItem())

#     class Meta:
#         template = "blocks/testimonial_section_block.html"


# class BlogSectionBlock(StructBlockBase):
#     title = blocks.CharBlock()
#     body = blocks.RichTextBlock(required=False)
#     badges = blocks.ListBlock(BadgeTextBlock())
#     limit = blocks.IntegerBlock(default=5, min_value=4, max_value=10, label="Blog Post Limit")
#     read_all_btn_text = blocks.CharBlock(default="Read More Guides", label="Visit Blog (Button Text)")

#     def get_context(self, value, parent_context=None):
#         context = super().get_context(value, parent_context)
#         BlogPost = apps.get_model("blog_manager", "blogpostpage")
#         blog_posts = BlogPost.objects.live().order_by("first_published_at")
#         limit = value.get("limit")
#         if limit:
#             blog_posts = blog_posts[:limit]
#         context["blog_posts"] = blog_posts
#         return context

#     class Meta:
#         template = "blocks/blog_section_block.html"


# class FAQSectionBlock(FAQBlock):
#     badges = blocks.ListBlock(BadgeTextBlock(), required=False)

#     class Meta:
#         template = "blocks/faq_section_block.html"


# class FounderBlock(blocks.StructBlock):
#     image = ImageChooserBlock(required=False)
#     name = blocks.CharBlock()
#     designation = blocks.CharBlock()
#     linkedin_profile_url = blocks.URLBlock(required=False)


# class FoundersSectionBlock(StreamBlockBase):
#     title = blocks.CharBlock()
#     content = blocks.RichTextBlock(required=False)
#     founders = blocks.ListBlock(FounderBlock())

#     def get_context(self, value, parent_context=None):
#         context = super().get_context(value, parent_context)
#         from common.settings import SiteSettings
#         context['placeholder_image'] = SiteSettings.objects.first().placeholder_image
#         return context

#     class Meta:
#         template = "blocks/founders_section_block.html"


# class VisionMissionBlock(blocks.StructBlock):
#     title = blocks.CharBlock()
#     content = blocks.RichTextBlock()


# class VisionMissionBlock(StreamBlockBase):
#     vision = VisionMissionBlock()
#     mission = VisionMissionBlock()

#     class Meta:
#         template = "blocks/vision_mission_block.html"


# class ContainerBlock(blocks.StreamBlock):
#     body = blocks.RichTextBlock()

#     class Meta:
#         template = "blocks/container_block.html"


class CustomBlock(BlocksBase):
    # title = TitleBlock()
    # section_title = SectionTitleBlock()
    # button = ButtonBlock()
    # image_box = IconCardsBlock()
    # spacer = SpacerBlock()
    # badge_text = BadgeTextBlock()
    # faq_block = FAQBlock()
    # table_block = TableBlock()
    # container = ContainerBlock()
    home_hero_section = HomeHeroSection(group="Sections")
    icon_cards = IconCards(group="Sections")
    featured_products = FeaturedProductsSection(group="Sections")
    best_selling_products = BestSellingProductsSection(group="Sections")
    material_cards = MaterialCards(group="Sections")
    image_block = ImageBlock(group="Sections")
    two_column_image_block = TwoColumnImageBlock(group="Sections")
    mattress_benefits = MattressBenefitsSection(group="Sections")
    mattress_sizes = MattressSizeSection(group="Sections")
    faq_section = FAQBlock(group="Sections")
    cta_block = CTABlock(group="CTA")
    # hero_section = HeroSectionBlock(group="Sections")
    # hero_section_general = HeroSectionGeneral(group="Sections")
    # small_about = SmallAboutBlock(group="Sections")
    # featured_services = FeaturedServices(group="Sections")
    # all_services = AllServices(group="Sections")
    # filing_steps = FilingSteps(group="Sections")
    # clients_section = ClientSectionBlock(group="Sections")
    # our_services_small = OurServicesSmallBlock(group="Sections")
    # benefits_section = BenefitsSectionBlock(group="Sections")
    # testimonials_section = TestimonialSectionBlock(group="Sections")
    # blog_section = BlogSectionBlock(group="Sections")
    # faq_section = FAQSectionBlock(group="Sections")
    # founders_section = FoundersSectionBlock(group="Sections")
    # vision_mission_section = VisionMissionBlock(group="Sections")
    # snippet_chooser = SnippetChooserBlock(target_model="common.CommonSnippet", label="Common Snippets", group="Snippets")


class ProductDescriptionBlock(BlocksBase):
    product_description_gallery = ProductDescriptionGallery()
