from django.http import HttpResponse
from django.template import loader

from . import models 
from customer.models import Product

from django.shortcuts import render


def guest(request):
  template = loader.get_template('guest.html')
  return HttpResponse(template.render())

def index(request):
    if request.customer_id is not None:
        # A customer is logged in, use their customer_id and username
        customer_id = request.customer_id
        customer_username = request.customer_username
        return render(request, 'index.html', {'customer_id': customer_id, 'customer_username': customer_username})
    else:
        # Guest user, you can handle this case differently if needed
        return render(request, 'index.html', {'customer_id': None, 'customer_username': "Guest"})


def products(request):
    # Query the Product model or perform any other operations
    products = Product.objects.all()
    # Render the template with the products
    return render(request, 'products.html', {'products': products})