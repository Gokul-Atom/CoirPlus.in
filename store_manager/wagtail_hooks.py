from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import Product, Category, Attribute, AttributeValue


class CategoryAdmin(ModelAdmin):
    model = Category
    menu_label = "Categories"
    menu_icon = "form"
    search_fields = ("title",)


class ProductAdmin(ModelAdmin):
    model = Product
    menu_label = "Products"
    menu_icon = "form"
    search_fields = ("title",)


class AttributeAdmin(ModelAdmin):
    model = Attribute
    menu_icon = "folder"
    menu_label = "Attributes"
    search_fields = ("name", "attribute_values__value")


class StoreAdmin(ModelAdminGroup):
    menu_label = "E-Com Store"
    menu_icon = "store"
    menu_order = 100
    items = (ProductAdmin, CategoryAdmin, AttributeAdmin)
modeladmin_register(StoreAdmin)
