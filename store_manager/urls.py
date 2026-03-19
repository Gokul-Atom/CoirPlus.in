from django.urls import path
from . import views


urlpatterns = [
    path("product/<str:slug>/", view=views.product_page, name="product_page"),
    path("api/product-variation/<int:variation_id>/price/", view=views.get_product_variation_price, name="get_product_variation_price"),
    path("api/reviews/<int:product_id>/add/", view=views.add_review, name="add_review"),
    path("api/reviews/<int:product_id>/", view=views.get_reviews, name="get_reviews"),
    path("api/reviews/<int:review_id>/delete/", view=views.delete_review, name="delete_review"),
]
