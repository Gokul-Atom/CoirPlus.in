from django.urls import reverse
import razorpay
from salesman.checkout.payment import PaymentMethod
from salesman.core.utils import get_salesman_model
from common.settings import SiteSettings
from django.http import HttpResponse

Order = get_salesman_model("Order")

class RazorpayAPI:
    def __init__(self):
        self.test_api_key = None
        self.test_api_secret = None
        self.live_api_key = None
        self.live_api_secret = None
        self.client = None

    def authorize_client(self):
        site_settings = SiteSettings.load()
        self.live_api_key = site_settings.live_api_key
        self.live_api_secret = site_settings.live_api_secret
        self.test_api_key = site_settings.test_api_key
        self.test_api_secret = site_settings.test_api_secret
        if site_settings.enable_razorpay:
            if site_settings.enable_live_mode:
                self.client = razorpay.Client(auth=(self.live_api_key, self.live_api_secret))
            else:
                self.client = razorpay.Client(auth=(self.test_api_key, self.test_api_secret))

    def create_order(self, amount, order):
        if self.client is None:
            self.authorize_client()
        return self.client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1",
            "receipt": order.ref,
        })
    
    def verify_payment_signature(self, params_dict):
        try:
            if self.client is None:
                self.authorize_client()
            self.client.utility.verify_payment_signature(params_dict)
            # except AttributeError:
            #     return False
            return True
        except razorpay.errors.SignatureVerificationError as e:
            print(e)
            return False

razorpay_api = RazorpayAPI()


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
    
    def verify_payment_signature(self, params_dict):
        razorpay_api = RazorpayAPI()
        razorpay_api.authorize_client()
        return razorpay_api.verify_payment_signature(params_dict)

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
        razorpay_order = razorpay_api.create_order(amount, order)
        order.razorpay_order_id = razorpay_order["id"]
        email = kwargs.get("email")
        billing_address = kwargs.get("billing_address")
        shipping_address = kwargs.get("shipping_address") or kwargs.get("billing_address")
        phone_number = kwargs.get("phone_number")
        order.extra["phone_number"] = phone_number
        order_notes = kwargs.get("order_notes")
        if order_notes:
            OrderNote = get_salesman_model('OrderNote')
            OrderNote.objects.create(
                order=order,
                message="This is a customer note.",
                public=True  # Set to False for internal notes
            )
        if email:
            order.email = email
        if billing_address:
            order.billing_address = billing_address.plain_address()
        if shipping_address:
            order.shipping_address = shipping_address.plain_address() if shipping_address else billing_address.plain_address()
        order.save()
        # basket.items.all().delete()
        return order
        # url = reverse("salesman-order-last") + f"?token={order.token}"
        if request.headers.get("HX-Request"):
            response = HttpResponse()
            response["HX-Redirect"] = f"https://api.razorpay.com/v1/checkout/public?order_id={order.razorpay_order_id}"
            return response
        return f"https://api.razorpay.com/v1/checkout/public?order_id=order_SSfqUQcp6XFhWF"
        # return request.build_absolute_uri(url)