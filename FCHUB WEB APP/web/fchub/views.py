from django.shortcuts import get_object_or_404, redirect, render
from django.core.cache import cache
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from customer.models import Customer, Order, Product, OrderItem
from .models import Material, FleekyAdmin, Category, Tracker 
from .forms import FleekyAdminForm, MaterialForm, ProductForm, TrackerForm
from django.contrib.auth.forms import UserCreationForm
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
def view_product(request):
    # Get the selected sorting option from the GET request
    sort_option = request.GET.get('sort')

    # Default to sorting by price low to high
    if sort_option == 'high_to_low':
        products = Product.objects.all().order_by('-price')
    else:
        products = Product.objects.all().order_by('price')

    return render(request, 'view/products.html', {'products': products})

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
def delete_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    if request.method == 'POST':
        product.delete()
        return redirect('fchub:products')  # Redirect to the list of products after deleting
    
    return render(request, 'delete/delete-product.html', {'product': product})

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







def view_materials(request):
    materials=Material.objects.all()
    return render(request,'view/materials.html',{'materials':materials})

def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            print("Material saved successfully")  # Add a print statement for debugging
            return redirect('fchub:materials')
        else:
            print("Form is not valid")  # Add a print statement for debugging
    else:
        form = MaterialForm()

    return render(request, 'add/add-material.html', {'form': form})

def delete_material(request, pk):
    material = get_object_or_404(Material, id=pk)
    
    if request.method == 'POST':
        material.delete()
        return redirect('fchub:materials')  # Redirect to the list of materials after deleting
    
    return render(request, 'delete/delete-material.html', {'material': material})

def edit_material(request, material_id):
    material = Material.objects.get(id=material_id)

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect('fchub:materials')
    else:
        form = MaterialForm(instance=material)

    return render(request, 'edit/edit-material.html', {'form': form})




def view_purchase(request):
    fabric_type = request.GET.get('fabric_type')
    payment = request.GET.get('payment')
    price = request.GET.get('price')
    color = request.GET.get('color')
    product_tag = request.GET.get('product_tag')
    set_tag = request.GET.get('set_tag')
    month_of_purchase = request.GET.get('month_of_purchase')
    qty = request.GET.get('qty')
    count = request.GET.get('count')

    purchases = Tracker.objects.all()

    if fabric_type:
        purchases = purchases.filter(fabric_type=fabric_type)
    if payment:
        purchases = purchases.filter(payment=payment)
    if price == 'low_to_high':
        purchases = purchases.order_by('price')
    elif price == 'high_to_low':
        purchases = purchases.order_by('-price')
    if color:
        purchases = purchases.filter(color=color)
    if product_tag:
        purchases = purchases.filter(product_tag=product_tag)
    if set_tag:
        purchases = purchases.filter(set_tag=set_tag)
    if month_of_purchase:
        purchases = purchases.filter(month_of_purchase=month_of_purchase)
    if qty:
        purchases = purchases.filter(qty=qty)
    if count == 'low_to_high':
        purchases = purchases.order_by('count')
    elif count == 'high_to_low':
        purchases = purchases.order_by('-count')

    return render(request, 'view/track-purchase.html', {'purchases': purchases})

# Add a new purchase record
def add_purchase(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fchub:track-purchase')
    else:
        form = TrackerForm()
    return render(request, 'add/add-purchase.html', {'form': form})

# Edit an existing purchase record
def edit_purchase(request, purchase_id):
    purchase = Tracker.objects.get(id=purchase_id)
    if request.method == 'POST':
        form = TrackerForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            return redirect('fchub:track-purchase')
    else:
        form = TrackerForm(instance=purchase)
    return render(request, 'edit/edit-purchase.html', {'form': form, 'purchase': purchase})

# Delete a purchase record
def delete_purchase(request, purchase_id):
    purchase = Tracker.objects.get(id=purchase_id)
    
    if request.method == 'POST':
        purchase.delete()
        return redirect('fchub:track-purchase')  # Redirect to the list of purchases after deleting
    
    return render(request, 'delete/delete-purchase.html', {'purchase': purchase})








def view_manage_business(request):
    active = request.user.fleekyadmin
    return render(request,'manage-business/manage-business.html', {'active':active})








def list_admins(request):
    admins = FleekyAdmin.objects.all()
    return render(request, 'view/users-admin.html', {'admins': admins})

def add_admin(request):
    if request.method == 'POST':
        # Create instances of UserCreationForm and FleekyAdminForm
        user_form = UserCreationForm(request.POST)
        admin_form = FleekyAdminForm(request.POST)
        
        if user_form.is_valid() and admin_form.is_valid():
            # Save the user form to create a new user
            user = user_form.save()
            
            # Create a FleekyAdmin instance and link it to the user
            admin = admin_form.save(commit=False)
            admin.user = user
            admin.save()
            
            return redirect('fchub:list-admins')  # Redirect to the list of admins
    else:
        user_form = UserCreationForm()
        admin_form = FleekyAdminForm()
    
    return render(request, 'add/user-admin.html', {'user_form': user_form, 'admin_form': admin_form})

def delete_admin(request, pk):
    admin = get_object_or_404(FleekyAdmin, pk=pk)
    admin.delete()
    return redirect('list-admins')  # Redirect to the list of admins after deleting