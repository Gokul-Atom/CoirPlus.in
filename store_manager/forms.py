from .models import Review
from django import forms


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            'rating': forms.RadioSelect,
            'title': forms.TextInput(),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'rating': 'Rating',
            'title': 'Review Title',
            'comment': 'Your Review',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to ALL fields
        self.label_suffix = ""
        for field_name, field in self.fields.items():
            if field_name == "rating":
                field.widget.attrs['class'] = 'form-check-input form-input'
            else:
                field.widget.attrs['class'] = 'form-control form-input'
                field.label_class = 'form-label fw-semibold'
