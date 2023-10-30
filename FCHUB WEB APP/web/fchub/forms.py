from django import forms
from django.contrib.auth.models import User
from .models import Csv, Material, Product
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _
from .models import FleekyAdmin, Tracker


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

class FleekyAdminForm(forms.ModelForm):
    class Meta:
        model = FleekyAdmin
        fields = ['user', 'first_name', 'last_name', 'login_time', 'logout_time', 'is_customer', 'is_admin']

    def __init__(self, *args, **kwargs):
        super(FleekyAdminForm, self).__init__(*args, **kwargs)

        self.fields['user'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['login_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['logout_time'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_customer'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_admin'].widget.attrs.update({'class': 'form-check-input'})


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'unit', 'price', 'description']  # Customize as needed

class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = '__all__'  # Include all fields from the Tracker model in the form


class CsvUploadForm(forms.ModelForm):
    class Meta:
        model = Csv
        fields = ['csv_file']