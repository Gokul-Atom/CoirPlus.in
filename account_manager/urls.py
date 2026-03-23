from django.urls import path
from . import views


urlpatterns = [
    path("checkout/", view=views.checkout_page, name="checkout"),
    path("payment/success/<str:token>/", view=views.payment_success_view, name="payment_success"),
    path("payment/<str:token>/", view=views.payment_page, name="payment_page"),
    path("api/wishlist/quantity/", view=views.get_wishlist_quantity, name="get_wishlist_quantity"),
    path("api/wishlist/", view=views.get_wishlist, name="get_wishlist"),
    path("api/wishlist-to-basket/", view=views.add_from_wishlist, name="add_from_wishlist"),
    path("api/wishlist/<int:variation_id>/", view=views.toggle_wishlist, name="toggle_wishlist"),
    path("my-account/orders/", view=views.my_orders, name="my_orders"),
    path("my-account/orders/<str:order_ref>/", view=views.view_order, name="view_order"),
    path("my-account/addresses/update/<int:address_id>/", view=views.update_user_address, name="update_user_address"),
    path("my-account/addresses/", view=views.my_addresses, name="my_addresses"),
    path("my-account/account-details/", view=views.my_account_details, name="my_account_details"),
]
