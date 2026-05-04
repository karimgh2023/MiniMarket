from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Listing


class BootstrapMixin:
    """Apply Bootstrap 5 field classes to all widgets."""

    control_class = "form-control"
    select_class = "form-select"

    def _style_widgets(self):
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", self.select_class)
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault("class", self.control_class)
            else:
                widget.attrs.setdefault("class", self.control_class)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_widgets()


class ListingForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["category", "title", "description", "price", "location", "image"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class StyledAuthenticationForm(BootstrapMixin, AuthenticationForm):
    pass


class RegisterForm(BootstrapMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
