from django import forms
from django import apps

from .models import Contact


class ContactForm(forms.ModelForm):
    Contact = apps.apps.get_model("support_manager", "Contact")
    class Meta:
        model = Contact
        fields = ("full_name", "subject", "message")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"