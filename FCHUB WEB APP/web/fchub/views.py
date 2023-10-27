from django.shortcuts import get_object_or_404, redirect, render
from django.core.cache import cache
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from customer.models import Customer, Order, Product, OrderItem
from .models import Material, FleekyAdmin, Category 
from .forms import ProductForm
# Create your views here.
def dashboard(request):
    active = request.user.fleekyadmin
    return render(request, 'dashboard.html', {'active': active})

def fchub_logout(request):
    logout(request)
    cache.clear()  # Clear the cache for all users
    return redirect('guest:index')


def view_customer(request):
    customers = Customer.objects.all()
    addresses = [customer.address for customer in customers if customer.address is not None]
    return render(request, 'view/customers.html', {'customers': customers, 'addresses': addresses})

def view_order(request):
    orders = Order.objects.all()
    data = []
    
    for order in orders:
        ordered_products = OrderItem.objects.filter(order=order)
        ordered_by = Customer.objects.filter(id=order.customer.id)
        data.append((ordered_products, ordered_by, order))
    
    return render(request, 'view/orders.html', {'data': data})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('fchub:products')  # Adjust this URL name as needed
    else:
        form = ProductForm()
    return render(request, 'add/add-product.html', {'form': form})

@login_required
def delete_product(request,pk):
    try:
        product = Product.objects.get(id=pk)
        product.delete()
    except Product.DoesNotExist:
        # Handle the case where the product with the given ID does not exist
        pass

    return redirect('fchub:products')

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('fchub:products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit/edit-product.html', {'form': form})





@login_required
def view_product(request):
    products = Product.objects.all()
    return render(request, 'view/products.html', {'products': products})

def view_materials(request):
    materials=Material.objects.all()
    return render(request,'view/materials.html',{'Materials':materials})


def view_manage_business(request):
    active = request.user.fleekyadmin
    return render(request,'manage-business/manage-business.html', {'active':active})
