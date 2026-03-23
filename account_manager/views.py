from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from store_manager.models import Basket, Order
from account_manager.forms import CheckoutAddressForm
from salesman.checkout.payment import payment_methods_pool
from salesman.core.utils import get_salesman_model
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib import messages

from store_manager.models import ProductVariation
from store_manager.serializers import ProductVariationSerializer
from .models import CheckoutAddress
from .forms import CheckoutAddressForm
from common.settings import SiteSettings


# Create your views here.
@login_required
def checkout_page(request):
    basket = get_object_or_404(Basket, user=request.user)
    if request.method == "POST":
        different_shipping_address = request.POST.get("different_shipping_address")
        print(different_shipping_address)
        billing_form = CheckoutAddressForm(request.POST, prefix="billing")
        shipping_form = CheckoutAddressForm(request.POST, prefix="shipping")
        payment_identifier = request.POST.get("payment-method")
        order_notes = request.POST.get("order-notes")
        print(request.POST)
        if billing_form.is_valid():
            billing = billing_form.save(commit=False)
            billing.user = request.user
            billing.save()
            if different_shipping_address and shipping_form.is_valid():
                shipping = shipping_form.save(commit=False)
                shipping.user = request.user
                shipping.save()
            else:
                shipping = None
            try:
                payment_method = payment_methods_pool.get_payment(payment_identifier)
                order = payment_method.basket_payment(
                    basket,
                    request,
                    shipping_address=shipping,
                    billing_address=billing,
                    email=shipping.email if shipping else billing.email,
                    phone_number=shipping.phone_number if shipping else billing.phone_number,
                    order_notes=order_notes,
                    )
                if request.headers.get("HX-Request"):
                    context= {
                        "different_shipping_address": bool(different_shipping_address),
                        "shipping_form": shipping_form,
                        "billing_form": billing_form,
                    }
                    response = TemplateResponse(request, "components/checkout_form.html", context=context)
                    response["HX-Redirect"] = reverse("payment_page", kwargs={"token": order.token})
                    return response
                return redirect("payment_page", token=order.token)
            except Exception as e:
                print(e)
                raise ValidationError("Invalid or disabled payment method.")
        else:
            context= {
                "different_shipping_address": bool(different_shipping_address),
                "shipping_form": shipping_form,
                "billing_form": billing_form,
            }
            if request.headers.get("HX-Request"):
                return TemplateResponse(request, "components/checkout_form.html", context=context)
            return render(request, "account_manager/checkout_page.html", context=context)

            # return redirect("success")
    else:
        shipping_form = CheckoutAddressForm(prefix="shipping")
        billing_form = CheckoutAddressForm(prefix="billing")

    return render(request, "account_manager/checkout_page.html", {
        "shipping_form": shipping_form,
        "billing_form": billing_form,
    })


@login_required
def payment_page(request, token):
    order = Order.objects.filter(token=token).first()
    common_settings = SiteSettings.load()
    context = {
        "order": order,
        "razorpay_api_key": common_settings.live_api_key if common_settings.enable_live_mode else common_settings.test_api_key
    }
    print(order)
    return TemplateResponse(request, "account_manager/payment_page.html", context=context)


@login_required
@csrf_exempt
def payment_success_view(request, token):
    order = Order.objects.filter(token=token).first()
    data = request.POST
    order_id = data.get('razorpay_order_id')
    payment_id = data.get('razorpay_payment_id')
    signature = data.get('razorpay_signature')
    print(data)
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature,
    }
    payment_method = payment_methods_pool.get_payment("razorpay")
    result = payment_method.verify_payment_signature(params_dict)
    if result:
        order.pay(order.total, payment_method="razorpay", transaction_id=payment_id)
        order.razorpay_payment_id = payment_id
        order.status = "PAID"
        order.save()
        messages.success(request, "Payment Success", extra_tags="success")
        # return render(request, 'account_manager/payment_success.html')
    else:
        messages.error(request, "Payment Failed", extra_tags="danger")
    return redirect("my_orders")
    # return render(request, 'account_manager/payment_failure.html')


@login_required
@api_view(["POST"])
def toggle_wishlist(request, variation_id):
    variation = get_object_or_404(ProductVariation, id=variation_id)
    user = request.user
    data = {}
    if user in variation.wishlisted_by.all():
        variation.wishlisted_by.remove(user)
        data = {"id": variation_id, "status": -1}
    else:
        variation.wishlisted_by.add(user)
        data = {"id": variation_id, "status": 1}
    variation.save(update_fields=["wishlisted_by"])
    if "wishlist" in request.query_params:
        return redirect("get_wishlist")
    return Response(data)

@login_required
@api_view(["GET", "POST"])
def update_user_address(request, address_id):
    address = get_object_or_404(CheckoutAddress, id=address_id)
    form = CheckoutAddressForm(instance=address)
    context = {
        "form": form
    }
    return TemplateResponse(request, "components/form_template.html", context=context)


@login_required
@api_view(["GET"])
def get_wishlist(request):
    wishlist = request.user.wishlisted_products.all()
    serializer = ProductVariationSerializer(wishlist, many=True)
    return Response(serializer.data)


@login_required
@api_view(["GET"])
def get_wishlist_quantity(request):
    wishlist = request.user.wishlisted_products.all()
    return Response({"quantity": wishlist.count()})


@login_required
@api_view(["POST"])
def add_from_wishlist(request):
    wishlist = request.user.wishlisted_products.all()
    Basket = get_salesman_model("Basket")
    basket, created = Basket.objects.get_or_create_from_request(request)
    variation = get_object_or_404(ProductVariation, id=request.POST.get("product_id"))
    basket.add(
        product=variation,
        quantity=int(request.POST.get("quantity")),
    )
    serializer = ProductVariationSerializer(wishlist, many=True)
    return Response(serializer.data)


@login_required
def my_orders(request):
    context = {}
    return TemplateResponse(request, "account_manager/my_orders.html", context=context)


@login_required
def view_order(request, order_ref):
    order = get_object_or_404(Order, ref=order_ref, user=request.user)
    context = {"order": order}
    return TemplateResponse(request, "account_manager/view_order.html", context=context)


@login_required
def my_addresses(request):
    context = {}
    return TemplateResponse(request, "account_manager/my_addresses.html", context=context)


@login_required
def my_account_details(request):
    context = {}
    return TemplateResponse(request, "account_manager/my_account_details.html", context=context)
