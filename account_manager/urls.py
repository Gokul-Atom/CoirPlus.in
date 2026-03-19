from django.urls import path
from . import views


urlpatterns = [
    path("checkout/", view=views.checkout_page, name="checkout"),
    path("payment/success/<str:token>/", view=views.payment_success_view, name="payment_success"),
    path("payment/<str:token>/", view=views.payment_page, name="payment_page"),
]
