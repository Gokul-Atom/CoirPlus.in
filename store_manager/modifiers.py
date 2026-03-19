from decimal import Decimal
from salesman.basket.modifiers import BasketModifier


# class DiscountModifier(BasketModifier):
#     """
#     Apply 10% discount on entire basket.
#     """

#     identifier = "discount"

#     def process_basket(self, basket, request):
#         if basket.count:
#             amount = basket.subtotal / -10
#             self.add_extra_row(basket, request, label="Discount 10%", amount=amount)


# class SpecialTaxModifier(BasketModifier):
#     """
#     Add 10% tax on items with price grater than 99.
#     """

#     identifier = "special-tax"

#     def process_item(self, item, request):
#         if item.total > 99:
#             label = "Special tax"
#             amount = item.total / 10
#             extra = {"message": f"Price threshold is exceeded by {item.total - 99}"}
#             self.add_extra_row(item, request, label, amount, extra)


# class ShippingCostModifier(BasketModifier):
#     """
#     Add flat shipping cost to the basket.
#     """

#     identifier = "shipping-cost"

#     def process_basket(self, basket, request):
#         if basket.count:
#             self.add_extra_row(basket, request, label="Shipping", amount=30)


class TaxModifier(BasketModifier):
    """
    Apply GST and CGST tax
    """
    identifier = "tax"
    
    def process_basket(self, basket, request):
        return super().process_basket(basket, request)
    


class GSTBasketModifier(BasketModifier):
    """
    Add CGST + SGST (e.g., 9% + 9% = 18% total GST) to the basket.
    Extra rows appear in `basket.extra_rows` and update `basket.total`.
    """

    identifier = "gst"  # unique identifier for settings

    # Common India GST rate (can also be made dynamic per product later)
    CGST_RATE = Decimal("0.09")
    SGST_RATE = Decimal("0.09")
    GST_RATE = CGST_RATE + SGST_RATE  # 18%

    def process_basket(self, basket, request):
        """
        Called once per basket when modifiers are applied.
        """
        if not basket.count:
            return

        # Remove any existing GST extra rows so we don't double‑add
        for key in list(basket.extra_rows.keys()):
            if key.startswith("gst:"):
                del basket.extra_rows[key]

        # 1. CGST on basket subtotal
        cgst_amount = basket.subtotal * self.CGST_RATE
        if cgst_amount:
            self.add_extra_row(
                basket,
                request,
                label=f"CGST ({self.CGST_RATE * 100:.0f}%)",
                amount=cgst_amount,
                identifier="gst:cgst",
            )

        # 2. SGST on basket subtotal
        sgst_amount = basket.subtotal * self.SGST_RATE
        if sgst_amount:
            self.add_extra_row(
                basket,
                request,
                label=f"SGST ({self.SGST_RATE * 100:.0f}%)",
                amount=sgst_amount,
                identifier="gst:sgst",
            )

        # 3. Recalculate total: subtotal + CGST + SGST
        basket.total = (
            basket.subtotal
            + cgst_amount
            + sgst_amount
        )
