from django import forms
from django.contrib.auth.models import User
from .models import Customer, Address, Product, Cart,  Payment, CartItem, Order
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

