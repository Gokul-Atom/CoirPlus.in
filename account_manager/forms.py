from django import forms
from .models import CheckoutAddress

class BillingForm(forms.ModelForm):
    class Meta:
        model = CheckoutAddress
        fields = "__all__"
        exclude = ("user", )
        widgets = {
            "is_billing": forms.HiddenInput(),
            "is_shipping": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        for field_name, field in self.fields.items():
            if field_name == "country":
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     if not cleaned_data["first_name"]:
    #         rais


class ShippingForm(forms.ModelForm):
    class Meta:
        model = CheckoutAddress
        fields = "__all__"
        exclude = ("user", )
        widgets = {
            "is_billing": forms.HiddenInput(),
            "is_shipping": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        for field_name, field in self.fields.items():
            if field_name == "country":
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data["is_shipping"]:
            return
        return cleaned_data
    

class CheckoutAddressForm(forms.ModelForm):
    # is_shipping = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    # is_billing = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    class Meta:
        model = CheckoutAddress
        fields = "__all__"
        exclude = ("user", )
        widgets = {
            "is_billing": forms.CheckboxInput(),
            "is_shipping": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        print("init", self.prefix)
        # if self.prefix == "shipping":
        #    self.initial["is_shipping"] = True
        if self.prefix == "billing":
            self.initial["is_billing"] = True
        for field_name, field in self.fields.items():
            if field_name == "country":
                field.widget.attrs["class"] = "form-select"
            elif field_name == "is_shipping" or field_name == "is_billing":
                field.widget.attrs["class"] = "d-none"
            else:
                field.widget.attrs["class"] = "form-control"
    
    def clean(self):
        cleaned_data = super().clean()
        # print(cleaned_data)
        if self.prefix == "shipping" and not cleaned_data.get("is_shipping"):
            return cleaned_data
        required_fields = [
            "first_name",
            "email",
            "address1",
            "city",
            "state",
            "country",
            "zip",
            "phone_number",
        ]

        for field_name in required_fields:
            value = cleaned_data.get(field_name)
            if not value or value.strip() == "":
                self.add_error(field_name, "This field is required.")

        return cleaned_data