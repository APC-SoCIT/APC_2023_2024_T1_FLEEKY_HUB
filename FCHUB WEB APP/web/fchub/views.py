
from decimal import Decimal
from io import TextIOWrapper
import io
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.cache import cache
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from customer.models import Address, Customer, Order, Product, OrderItem
from .models import CsvData, Material, FleekyAdmin, Category, Tracker, User
from .forms import  CategoryForm, CsvUploadForm, FleekyAdminForm, MaterialForm, ProductForm, TrackerForm
from django.contrib.auth.forms import UserCreationForm
from .models import Csv  # Make sure you have this import
import csv
from .models import CsvData
from django.contrib import messages
import os
from django.db.models import Q
from django.core.exceptions import ValidationError
from datetime import datetime
from xhtml2pdf import pisa
from django.template.loader import get_template

# Create your views here.


def dashboard(request):
    # Calculate the counts
    customer_count = Customer.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    pending_order_count = Order.objects.filter(status='Pending').count()
    # Fetch the 5 most recent orders
    orders = Order.objects.all().order_by('-order_date')[:5]
    
    # Prepare lists for ordered products and ordered by
    ordered_products = []
    ordered_bys = []

    for order in orders:
        ordered_items = OrderItem.objects.filter(order=order)
        products = [item.product for item in ordered_items]
        customer = Customer.objects.get(user=order.customer)
        ordered_products.append(products)
        ordered_bys.append(customer)

    context = {
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'pending_order_count': pending_order_count,
        'data': zip(ordered_products, ordered_bys, orders),
    }

    return render(request, 'dashboard.html', context)

def fchub_logout(request):
    logout(request)
    cache.clear()  # Clear the cache for all users
    return redirect('guest:index')


def view_customer(request):
    customers = Customer.objects.all()   
    return render(request, 'view/customers.html', {'customers': customers})


def view_order(request):
    # Get filter parameters from the request
    order_date_filter = request.GET.get('order_date')
    order_status_filter = request.GET.get('order_status')  # Updated filter parameter
    total_price_filter = request.GET.get('total_price')
    payment_type_filter = request.GET.get('payment_type')

    # Start with an initial queryset of all orders
    orders = Order.objects.all()
    STATUS_CHOICES = Order.STATUS_CHOICES 
    # Apply filters based on user input
    if order_date_filter:
        try:
            # Assuming 'order_date' is a DateField in the Order model
            # Convert the input date to a datetime.date object
            order_date_filter = datetime.strptime(order_date_filter, '%Y-%m-%d').date()
            # Filter orders where the order date matches the input date
            orders = orders.filter(order_date=order_date_filter)
        except ValueError:
            # Handle invalid date format gracefully (you can show an error message)
            pass

    if order_status_filter:  # Check if the filter parameter is not empty
        # Filter orders where the status matches the input status
        orders = orders.filter(status=order_status_filter)

    if total_price_filter == "low_to_high":
        # Assuming 'total_price' is a field in the Order model
        orders = orders.order_by('total_price')
    elif total_price_filter == "high_to_low":
        orders = orders.order_by('-total_price')

    if payment_type_filter:
        # Assuming 'payment_method' is a field in the Order model
        if payment_type_filter == 'Online Payment':
            # Correct the filter value to match your model
            orders = orders.filter(payment_method='Online Payment')
        elif payment_type_filter == 'Cash on Delivery (COD)':
            orders = orders.filter(payment_method='Cash on Delivery (COD)')

    # Annotate each order with the sum of total item prices
    orders = orders.annotate(total_item_price=Sum('order_items__item_total'))

    data = []

    for order in orders:
        ordered_items = order.order_items.all()
        ordered_by = Customer.objects.get(user=order.customer)
        data.append((ordered_items, ordered_by, order))

    return render(request, 'view/orders.html', {'data': data, 'status_choices': STATUS_CHOICES})

def update_status(request, order_id):
    # Get the order object based on the order_id
    order = Order.objects.get(id=order_id)

    # Check if the request method is POST
    if request.method == 'POST':
        new_status = request.POST.get('new_status')

        # Update the order status
        order.status = new_status
        order.save()

        # Redirect back to the 'update-status' view with the updated order_id
        return redirect('fchub:orders')

    # Pass STATUS_CHOICES to the template
    return render(request, 'update/update-status.html', {'order': order, 'status_choices': Order.STATUS_CHOICES})


def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

def generate_invoice(request, order_id):
    # Ensure the user is an admin or has the necessary permissions
    if not request.user.is_staff:
        return HttpResponse("Permission denied", status=403)

    # Fetch the order with the given order_id
    order = get_object_or_404(Order, id=order_id)

    # Retrieve related customer, address, and order items
    customer = order.customer
    shipping_address = order.shipping_address
    order_items = order.order_items.all()

    # Calculate the total price for the order
    total_price = sum(item.item_total for item in order_items)

    # Access the user-related fields from the customer's profile
    customer_profile = Customer.objects.get(user=order.customer)
    customer_address = get_object_or_404(Address, customer=customer_profile)

    # Calculate VAT and total with VAT
    vat_rate = Decimal('0.12')
    vat = total_price * vat_rate
    with_vat = total_price + vat

    # Determine the shipping fee based on the region
    f_region = customer_address.region
    shipping_fee = 0

    regions_three = ["National Capital Region (NCR)", "Region I (Ilocos Region)", "Region II (Cagayan Valley)",
                     "Region III (Central Luzon)", "Region IV-A (CALABARZON)", "Region V (Bicol Region)"]
    regions_four = ["Region VI (Western Visayas)", "Region VII (Central Visayas)", "Region VIII (Eastern Visayas)"]
    regions_five = ["Region IX (Zamboanga Peninsula)", "Region X (Northern Mindanao)",
                    "Region XI (Davao Region)", "Region XII (SOCCSKSARGEN)", "Region XIII (Caraga)",
                    "Cordillera Administrative Region (CAR)", "Autonomous Region in Muslim Mindanao (ARMM)"]

    if f_region in regions_three:
        shipping_fee = Decimal('300')
    elif f_region in regions_four:
        shipping_fee = Decimal('400')
    elif f_region in regions_five:
        shipping_fee = Decimal('500')

    # Calculate the total price including VAT and shipping fee
    total_price = with_vat + shipping_fee

    # Define context data to pass to the template
    context = {
        'customer': customer,
        'customer_profile': customer_profile,
        'shipping_address': shipping_address,
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'vat': vat,
        'with_vat': with_vat,
        'shipping_fee': shipping_fee,
    }

    # Render the HTML template as a PDF
    pdf = render_to_pdf('view/invoice.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="invoice.pdf"'
        return response

    return HttpResponse("Error rendering PDF", status=500)

def view_full_details(request, order_id):
    # Ensure the user is an admin or has the necessary permissions
    if not request.user.is_staff:
        return HttpResponse("Permission denied", status=403)

    # Fetch the order with the given order_id
    order = get_object_or_404(Order, id=order_id)

    # Retrieve related customer, address, and order items
    customer = order.customer
    shipping_address = order.shipping_address
    order_items = order.order_items.all()

    # Calculate the total price for the order
    total_price = sum(item.item_total for item in order_items)

    # Access the user-related fields from the customer's profile
    customer_profile = Customer.objects.get(user=order.customer)
    customer_address = get_object_or_404(Address, customer=customer_profile)

    # Calculate VAT and total with VAT
    vat_rate = Decimal('0.12')
    vat = total_price * vat_rate
    with_vat = total_price + vat

    # Determine the shipping fee based on the region
    f_region = customer_address.region
    shipping_fee = 0

    regions_three = ["National Capital Region (NCR)", "Region I (Ilocos Region)", "Region II (Cagayan Valley)",
                     "Region III (Central Luzon)", "Region IV-A (CALABARZON)", "Region V (Bicol Region)"]
    regions_four = ["Region VI (Western Visayas)", "Region VII (Central Visayas)", "Region VIII (Eastern Visayas)"]
    regions_five = ["Region IX (Zamboanga Peninsula)", "Region X (Northern Mindanao)",
                    "Region XI (Davao Region)", "Region XII (SOCCSKSARGEN)", "Region XIII (Caraga)",
                    "Cordillera Administrative Region (CAR)", "Autonomous Region in Muslim Mindanao (ARMM)"]

    if f_region in regions_three:
        shipping_fee = Decimal('300')
    elif f_region in regions_four:
        shipping_fee = Decimal('400')
    elif f_region in regions_five:
        shipping_fee = Decimal('500')

    # Calculate the total price including VAT and shipping fee
    total_price = with_vat + shipping_fee

    # Define context data to pass to the template
    context = {
        'customer': customer,
        'customer_profile': customer_profile,
        'shipping_address': shipping_address,
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'vat': vat,
        'with_vat': with_vat,
        'shipping_fee': shipping_fee,
    }

    return render(request, 'view/full-details.html', context)




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


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fchub:category')
    else:
        form = CategoryForm()
    return render(request, 'add/add-category.html', {'form': form})

def edit_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('fchub:category')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit/edit-category.html', {'form': form, 'category': category})

def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    return redirect('fchub:category')

def category_list(request):
    categories = Category.objects.all()
    fabric_choices = Category.FABRIC_CHOICES
    set_type_choices = Category.SET_TYPE_CHOICES

    fabric_filter = request.GET.get('fabric')
    set_type_filter = request.GET.get('set_type')

    if fabric_filter:
        categories = categories.filter(fabric=fabric_filter)
    if set_type_filter:
        categories = categories.filter(setType=set_type_filter)

    return render(request, 'view/category.html', {
        'categories': categories,
        'fabric_choices': fabric_choices,
        'set_type_choices': set_type_choices,
        'selected_fabric': fabric_filter,
        'selected_set_type': set_type_filter,
    })



def view_materials(request):
    materials=Material.objects.all()
    return render(request,'view/materials.html',{'materials':materials})

def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].lower()
            custom_material_id = name[:2] + datetime.now().strftime("%y%m%d%H")
            if Material.objects.filter(name=name).exists() or Material.objects.filter(Custom_material_id=custom_material_id).exists():
                # Display an error message if the material name or custom_material_id already exists (case-insensitive)
                messages.error(request, 'Material with this name or custom material ID already exists.')
            else:
                material = form.save(commit=False)
                material.name = name
                material.Custom_material_id = custom_material_id
                material.save()
                # Display a success message
                messages.success(request, 'Material saved successfully.')
                return redirect('fchub:materials')
        else:
            # Display an error message if the form is not valid
            messages.error(request, 'Form is not valid.')

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
    try:
        active = request.user.fleekyadmin
    except FleekyAdmin.DoesNotExist:
        active = None  # Handle the case when FleekyAdmin is missing
    return render(request,'manage-business/manage-business.html', {'active':active})

def parse_csv_data(csv_file):
    csv_data = []

    try:
        # Assuming csv_file is a File object
        # Read the CSV content from the file
        csv_content = csv_file.read().decode('utf-8')

        # Create a CSV reader
        csv_reader = csv.reader(io.StringIO(csv_content))

        # Limit the number of samples to 6
        sample_count = 0

        # Iterate through the rows and add them to csv_data
        for row in csv_reader:
            csv_data.append(row)
            sample_count += 1

            if sample_count >= 6:
                break

    except Exception as e:
        # Handle any exceptions that may occur during parsing
        # You can log the error or raise an appropriate exception
        pass

    return csv_data

ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.xlsm', '.xlsb', '.xltx', '.xltm', '.xlam', '.csv', '.ods', '.xml', '.txt', '.prn', '.dif', '.slk', '.htm', '.html', '.dbf', '.json'}

def upload_csv(request):
    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']

            # Check the file extension
            file_extension = os.path.splitext(csv_file.name)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                # Add an error message and reload the page
                messages.error(request, f'Unsupported file type: {file_extension}. Please upload a valid file.')
                return redirect('fchub:upload-csv')

            # Create a Csv object and save it with a unique name
            csv = Csv(csv_file=csv_file)
            csv.save()

            # Rename the file with a unique name
            csv.file_name = f'csv-{csv.id}-{csv.uploaded_at.strftime("%Y%m%d")}'
            csv.save()

            # Add a success message
            messages.success(request, 'CSV file uploaded successfully.')

            return redirect('fchub:upload-csv')

        else:
            # Add an error message
            messages.error(request, 'Error uploading CSV file. Please check the file format.')

    else:
        form = CsvUploadForm()

    # Get all uploaded CSV files
    csv_files = Csv.objects.all()

    # Fetch the most recent CSV entry
    most_recent_csv = Csv.objects.order_by('-uploaded_at').first()

    # Check if there is no uploaded file
    if not most_recent_csv:
        messages.info(request, 'Please upload a CSV file first.')  # Add this message
    else:
        # Parse the most recent CSV data (assuming it's a CSV string) into a list of lists
        most_recent_csv.csv_data = parse_csv_data(most_recent_csv.csv_file)

    recent_csv_files = Csv.objects.order_by('-uploaded_at')[:5]

    return render(request, 'manage-business/csv-template.html', {'form': form, 'recent_csv_files': recent_csv_files, 'csv_files': csv_files, 'most_recent_csv': most_recent_csv})

def delete_csv(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        try:
            csv_file = Csv.objects.get(id=file_id)
            # Delete the CSV file from your storage (if needed)
            csv_file.csv_file.delete()
            # Delete the Csv object from the database
            csv_file.delete()
        except Csv.DoesNotExist:
            # Handle the case where the CSV file does not exist
            pass

    return redirect('fchub:upload-csv')  # Redirect to the page where CSV files are listed






def users_admins(request):
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
            
            return redirect('fchub:users-admins')  # Redirect to the list of admins
    else:
        user_form = UserCreationForm()
        admin_form = FleekyAdminForm()
    
    return render(request, 'add/user-admin.html', {'user_form': user_form, 'admin_form': admin_form})

def delete_admin(request, pk):
    admin = get_object_or_404(FleekyAdmin, pk=pk)
    admin.delete()
    return redirect('fchub:users-admins')  # Redirect to the list of admins after deleting


