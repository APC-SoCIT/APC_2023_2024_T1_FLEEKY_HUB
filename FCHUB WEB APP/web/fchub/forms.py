from django import forms
from django.contrib.auth.models import User
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['custom_id']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Set all fields (except 'name') as not required
        for field_name, field in self.fields.items():
            if field_name != 'name':
                field.required = False