from django.urls import reverse
import razorpay
from salesman.checkout.payment import PaymentMethod
from salesman.core.utils import get_salesman_model
from common.settings import SiteSettings
from django.http import HttpResponse

Order = get_salesman_model("Order")


class Razorpay(PaymentMethod):
    """
    Payment method that requires advance payment via bank account.
    """

    identifier = "razorpay"
    label = "Razorpay"
    
    def __init__(self):
        self.client = None
        self.settings = None

    def load_settings(self):
        self.settings = SiteSettings.load()

    def is_enabled(self, *args, **kwargs):
        if self.settings is None:
            self.load_settings()
        """
        Return True if this payment method should be available for `basket` and `request`.
        Return False to hide it completely from the checkout options.
        """
        return self.settings.enable_razorpay
    
    def get_auth_credentials(self):
        api = None
        secret = None
        if self.settings is None:
            self.load_settings()
        if self.settings.enable_razorpay:
            api = self.settings.test_api_key
            secret = self.settings.test_api_secret
            if self.settings.enable_live_mode:
                api = self.settings.live_api_key
                secret = self.settings.live_api_secret
        return (api, secret)

    def authorize_client(self):
        self.client = razorpay.Client(auth=(self.get_auth_credentials()))
    
    def validate_basket(self, basket, request):
        super().validate_basket(basket, request)

    def basket_payment(self, basket, request, *args, **kwargs):
        """
        Create a new order and mark it on-hold. Reserve items from stock and await
        manual payment from customer via back account. When paid order status should be
        changed to `PROCESSING`, `SHIPPED` or `COMPLETED` and a new payment should be
        added to order.
        """
        self.authorize_client()
        basket.update(request)
        amount = int(basket.total * 100)
        order = Order.objects.create_from_basket(basket, request, status="HOLD")
        razorpay_order = self.client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1",
            "receipt": order.ref,
        })
        order.razorpay_order_id = razorpay_order["id"]
        email = kwargs.get("email")
        billing_address = kwargs.get("billing_address")
        shipping_address = kwargs.get("shipping_address")
        if email:
            order.email = email
        if billing_address:
            order.billing_address = billing_address.plain_address()
        if shipping_address:
            order.shipping_address = shipping_address.plain_address() if shipping_address else billing_address.plain_address()
        order.save(update_fields=["email", "billing_address", "shipping_address", "razorpay_order_id"])
        # basket.items.all().delete()
        return order
        # url = reverse("salesman-order-last") + f"?token={order.token}"
        if request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = f"https://api.razorpay.com/v1/checkout/public?order_id={order.razorpay_order_id}"
            return response
        return f"https://api.razorpay.com/v1/checkout/public?order_id=order_SSfqUQcp6XFhWF"
        # return request.build_absolute_uri(url)
    
    def verify_payment_signature(self, params_dict):
        try:
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError as e:
       # Payment signature verification failed
       # Handle the error accordingly
            return False