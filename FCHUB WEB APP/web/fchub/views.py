
import calendar
from decimal import Decimal
from io import TextIOWrapper
import io
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.cache import cache
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from customer.models import Address, Customer, Order, Product, OrderItem
from .models import CsvData, Material, FleekyAdmin, Category, SalesForCategory, SalesForColor, SalesForFabric, SalesForLocation, SalesForWebData, SuccessfulOrder, Tracker, User
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
import logging
from django.db import transaction
# Create your views here.

@login_required
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

@login_required
def view_customer(request):
    customers = Customer.objects.all()   
    return render(request, 'view/customers.html', {'customers': customers})

@login_required
def view_order(request):
    # Get filter parameters from the request
    order_date_filter = request.GET.get('order_date')
    order_status_filter = request.GET.get('order_status')
    total_price_filter = request.GET.get('total_price')
    payment_type_filter = request.GET.get('payment_type')
    order_id_filter = request.GET.get('order_id')  # New filter parameter for Order ID

    # Start with an initial queryset of all orders
    orders = Order.objects.all()
    STATUS_CHOICES = Order.STATUS_CHOICES

    # Apply filters based on user input
    if order_id_filter:  # Check if the filter parameter is not empty
        # Filter orders where the order ID matches the input Order ID
        orders = orders.filter(order_number=order_id_filter)

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


def calculate_count(setType, qty):
    # Define a dictionary to map set_type to its multiplier
    set_type_multipliers = {
        'Singles': 1,
        '3 in 1': 3,
        '4 in 1': 4,
        '5 in 1': 5,
    }

    # Calculate the count based on set_type and qty
    multiplier = set_type_multipliers.get(setType, 1)  # Default to 1 if set_type is not recognized
    return multiplier * qty


@login_required
def update_status(request, order_id):
    # Get the order object based on the order_id
    order = Order.objects.get(id=order_id)
    customer_profile = Customer.objects.get(user=order.customer)
    fname = customer_profile.first_name
    lname = customer_profile.last_name
    customer_name = fname + " " + lname

    # Check if the request method is POST
    if request.method == 'POST':
        new_status = request.POST.get('new_status')

        # Update the order status
        order.status = new_status
        order.save()

        # Check if the new status is "Delivered"
        if new_status == 'Delivered':
            # Check if a SuccessfulOrder with the same success_order_id already exists
            existing_successful_order = SuccessfulOrder.objects.filter(success_order_id=order.order_number).first()

            if existing_successful_order:
                # Prompt the user that it's already marked as delivered
                return render(request, 'update/already-delivered.html', {'order': order})

            # Retrieve additional information from related objects
            customer = order.customer
            address = order.shipping_address
            order_items = order.order_items.all()  # Retrieve all order items in the order

            # Aggregate fabric, setType, and color information from all products
            fabrics = ", ".join(order_item.product.category.fabric for order_item in order_items)
            setType = ", ".join(order_item.product.category.setType for order_item in order_items)
            colors = ", ".join(order_item.product.color for order_item in order_items)

            # Calculate the count based on set_type and qty for the ordered products
            total_count = sum(order_item.quantity for order_item in order_items)
            total_count_for_set_type = sum(calculate_count(order_item.product.category.setType, order_item.quantity) for order_item in order_items)

            # Calculate the price as the total_price of the order
            total_price = order.total_price

            # Create a SuccessfulOrder instance
            successful_order = SuccessfulOrder(
                order_number=order.order_number,
                date=order.order_date.date(),
                location=address.city + ", " + address.province,
                name=customer_name,
                fabric=fabrics,
                setType=setType,
                color=colors,
                qty=total_count,  # Quantity of each product
                count=total_count_for_set_type,  # Total count based on set type and quantity
                price=total_price
            )

            # Generate the success_order_id without foreign key relationship
            last_5_order_number = order.order_number[-5:]
            customer_name = customer.first_name[:3]
            username = customer.username[:3]
            location = address.detailed_address[:3]
            successful_order.success_order_id = f'SuccessfulOrder-{last_5_order_number}-{customer_name}-{username}-{location}'
            successful_order.save()

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

@login_required
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


@login_required
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
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fchub:category')
    else:
        form = CategoryForm()
    return render(request, 'add/add-category.html', {'form': form})


@login_required
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

@login_required
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    return redirect('fchub:category')

@login_required
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


@login_required
def view_materials(request):
    materials=Material.objects.all()
    return render(request,'view/materials.html',{'materials':materials})

@login_required
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


@login_required
def delete_material(request, pk):
    material = get_object_or_404(Material, id=pk)
    
    if request.method == 'POST':
        material.delete()
        return redirect('fchub:materials')  # Redirect to the list of materials after deleting
    
    return render(request, 'delete/delete-material.html', {'material': material})


@login_required
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



@login_required
def view_purchase(request):
    fabric_type = request.GET.get('fabric_type')
    payment = request.GET.get('payment')
    price = request.GET.get('price')
    color = request.GET.get('color')
    product_tag = request.GET.get('product_tag')
    setType = request.GET.get('setType')
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
    if setType:
        purchases = purchases.filter(setType=setType)
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
@login_required
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
@login_required
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
@login_required
def delete_purchase(request, purchase_id):
    purchase = Tracker.objects.get(id=purchase_id)
    
    if request.method == 'POST':
        purchase.delete()
        return redirect('fchub:track-purchase')  # Redirect to the list of purchases after deleting
    
    return render(request, 'delete/delete-purchase.html', {'purchase': purchase})







@login_required
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

            try:
                # Read the CSV content from the file
                csv_content = csv_file.read().decode('utf-8')

                # Create a Csv object and save it with a unique name
                csv = Csv(csv_file=csv_file)
                csv.save()

                # Rename the file with a unique name
                csv.file_name = f'csv-{csv.id}-{csv.uploaded_at.strftime("%Y%m%d")}'
                csv.save()

                # Add a success message
                messages.success(request, 'CSV file uploaded successfully.')
            except Exception as e:
                # Handle any exceptions that may occur during parsing
                # You can log the error or raise an appropriate exception
                messages.error(request, 'Error processing the uploaded CSV file.')

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
            if not csv_file.csv_file.closed:
                csv_file.csv_file.close()  # Close the file if it's open
            # Delete the Csv object from the database
            csv_file.delete()
        except Csv.DoesNotExist:
            # Handle the case where the CSV file does not exist
            pass

    return redirect('fchub:upload-csv')  # Redirect to the page where CSV files are listed


def parse_csv_for_migration(csv_content):
    # Create a list to store the CSV data
    data = []

    # Create a CSV reader
    csv_reader = csv.reader(io.StringIO(csv_content))

    # Skip the header row (if present)
    next(csv_reader, None)

    for row in csv_reader:
        data.append(row)

    return data

def migrate_csv_data(csv_data):
    try:
        # Iterate through the rows and create CsvData objects
        for row in csv_data:
            CsvData.objects.create(
                year=row[0],
                month=row[1],
                day=row[2],
                location=row[3],
                customerName=row[4],
                fabric=row[5],
                setType=row[6],
                color=row[7],
                quantity=row[8],
                count=row[9],
                price=row[10]
            )

    except Exception as e:
        # Handle any exceptions that may occur during migration
        print(f"Error during migration: {str(e)}")

def migrate_csv(request, csv_id):
    # Retrieve the Csv object with the provided ID
    csv = get_object_or_404(Csv, id=csv_id)

    # Ensure that csv.csv_file is a string by reading its content
    csv_content = csv.csv_file.read().decode('utf-8')

    # Parse the CSV content into a list of lists
    csv_data = parse_csv_for_migration(csv_content)

    if isinstance(csv_data, list):
        # Migrate CSV data to CsvData model
        migrate_csv_data(csv_data)

        # Redirect to the main CSV upload page with a success message
        messages.success(request, 'CSV data migrated to the database.')
        return redirect('fchub:upload-csv')
    else:
        # Handle the case where parse_csv_for_migration returned something other than a list
        return HttpResponseBadRequest('Invalid CSV data format')

def view_csv(request, file_id):
    # Fetch the CSV file from the database
    csv_file = get_object_or_404(Csv, id=file_id)

    # Parse the CSV file content
    csv_data = []
    try:
        csv_text = csv_file.csv_data
        csv_reader = csv.reader(csv_text.splitlines())
        for row in csv_reader:
            csv_data.append(row)
    except Exception as e:
        # Handle any exceptions (e.g., invalid CSV format)
        pass  # You should create an error template

    return render(request, 'csv-template.html', {'csv_data': csv_data, 'most_recent_csv': None})



def get_csv_data(request, file_id):
    try:
        # Retrieve the CSV file with the specified file_id
        csv_file = get_object_or_404(Csv, id=file_id)

        # Read the content from the csv_file field
        with open(csv_file.csv_file.path, 'rb') as file:
            csv_data = file.read()

        # You can customize the response content type based on your CSV data format
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{csv_file.file_name}.csv"'
        return response
    except Csv.DoesNotExist:
        # Handle the case where the CSV file does not exist
        return HttpResponse("CSV file not found.", status=404)


@login_required
def users_admins(request):
    admins = FleekyAdmin.objects.all()
    return render(request, 'view/users-admin.html', {'admins': admins})

@login_required
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

@login_required
def delete_admin(request, pk):
    admin = get_object_or_404(FleekyAdmin, pk=pk)
    admin.delete()
    return redirect('fchub:users-admins')  # Redirect to the list of admins after deleting


@login_required
def successful_orders(request):
    successful_orders = SuccessfulOrder.objects.all()
    return render(request, 'view/successful-orders.html', {'successful_orders': successful_orders})


@login_required
def download_successful_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="successful_orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['Year', 'Month', 'Day', 'Location', 'Name', 'Fabric', 'Set', 'Color', 'Qty', 'Count', 'Price'])

    successful_orders = SuccessfulOrder.objects.all()

    for order in successful_orders:
        year = order.date.year
        month = calendar.month_name[order.date.month]  # Convert month to string
        day = order.date.day
        writer.writerow([year, month, day, order.location, order.name, order.fabric, order.setType, order.color, order.qty, order.count, order.price])

    return response




MONTH_MAPPING = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12',
}
@login_required
def view_fchub_model(request):
    combined_data = SalesForWebData.objects.all()
    purchase_data = Tracker.objects.all()
    successful_orders = SuccessfulOrder.objects.all()
    
    # Add the following lines to retrieve data for the new models
    sales_for_fabric_data = SalesForFabric.objects.all()
    sales_for_category_data = SalesForCategory.objects.all()
    sales_for_location_data = SalesForLocation.objects.all()
    sales_for_color_data = SalesForColor.objects.all()

    parsed_combined_data = []

    for data in combined_data:
        if data.date:
            date_obj = datetime.strptime(data.date, "%Y-%m-%d")
            data.date = date_obj.strftime("%B")  # Update the 'date' field to the month

        # Split fabric, color, and set types if they contain multiple values
        fabrics = data.fabric_type.split(', ')
        colors = data.color.split(', ')
        set_types = data.set_type.split(', ')

        # Create separate rows for each combination
        for fabric in fabrics:
            for color in colors:
                for set_type in set_types:
                    parsed_data = SalesForWebData()
                    parsed_data.fabric_type = fabric
                    parsed_data.date = data.date  # Use the updated 'date' field
                    parsed_data.color = color
                    parsed_data.set_type = set_type
                    parsed_data.price = data.price
                    parsed_combined_data.append(parsed_data)

    context = {
        'parsed_combined_data': parsed_combined_data,
        'purchase_data': purchase_data,
        'successful_orders': successful_orders,
        'sales_for_fabric_data': sales_for_fabric_data,
        'sales_for_category_data': sales_for_category_data,
        'sales_for_location_data': sales_for_location_data,
        'sales_for_color_data': sales_for_color_data,
    }

    return render(request, 'manage-business/fchub-data-model.html', context)





def migrate_fchub_data(request):
    try:
        combined_data = []

        # Retrieve data from the SuccessfulOrder and Tracker models
        successful_orders = SuccessfulOrder.objects.all()
        tracker_data = Tracker.objects.all()

        # Iterate through SuccessfulOrder data
        for order in successful_orders:
            # For each SuccessfulOrder, create a SalesForWebData instance
            sales_data = SalesForWebData()
            sales_data.fabric_type = order.fabric
            sales_data.date = order.date
            sales_data.color = order.color
            sales_data.set_type = order.setType
            sales_data.price = order.price


            # Add the instance to the combined_data list
            combined_data.append(sales_data)

 
        # Iterate through Tracker data
        for data in tracker_data:
            # For each Tracker data, create a SalesForWebData instance
            sales_data = SalesForWebData()
            sales_data.fabric_type = data.fabric_type
            sales_data.location = data.month_of_purchase
            sales_data.color = data.color
            sales_data.set_type = data.setType
            sales_data.price = data.price

            # Add the instance to the combined_data list
            combined_data.append(sales_data)

        # Save the combined data to the SalesForWebData model
        SalesForWebData.objects.bulk_create(combined_data)


        messages.success(request, 'Combined data migrated successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')

    # Redirect to the 'fchub-data-model' view
    return HttpResponseRedirect(reverse('fchub:fchub-data-model'))


def delete_all_data(request):
    # Delete all records from the SalesForWebData model
    SalesForWebData.objects.all().delete()

    return redirect('fchub:fchub-data-model')



def migrate_fabric_data(request):
    try:
        combined_fabric = []

        combined_data = SalesForWebData.objects.all()

        # Iterate through SalesForWebData data
        for data in combined_data:
            # For each SalesForWebData instance, create a SalesForFabric instance
            sales_data = SalesForFabric()
            sales_data.fabric = data.fabric_type  # Correct the field name to 'fabric'
            sales_data.date = data.date
            sales_data.price = data.price

            # Save the instance to the combined_fabric list
            sales_data.save()
            combined_fabric.append(sales_data)

        messages.success(request, 'Combined data migrated successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')

    # Redirect to the 'fchub-data-model' view
    return HttpResponseRedirect(reverse('fchub:fchub-data-model'))


def migrate_category_data(request):
    try:
        combined_category = []

        combined_data = SalesForWebData.objects.all()

        # Iterate through SalesForCategory data
        for data in combined_data:
            # For each SalesForCategory instance, create a SalesForFabric instance
            sales_data = SalesForCategory()
            sales_data.set_tag = data.set_type
            sales_data.date = data.date
            sales_data.price = data.price

            # Save the instance to the combined_fabric list
            sales_data.save()
            combined_category.append(sales_data)

        messages.success(request, 'Category data migrated successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')

    # Redirect to the 'fchub-data-model' view (or update this as needed)
    return HttpResponseRedirect(reverse('fchub:fchub-data-model'))


def migrate_location_data(request):
    try:
        combined_location = []

        # Retrieve data from the SuccessfulOrder and CsvData models
        successful_orders = SuccessfulOrder.objects.all()
        csv_data = CsvData.objects.all()

        # Iterate through SuccessfulOrder data
        for order in successful_orders:
            # For each SuccessfulOrder, create a SalesForLocation instance
            sales_data = SalesForLocation()
            sales_data.date = order.date
            sales_data.fabric = order.fabric
            sales_data.set_type = order.setType
            sales_data.location = order.location
            sales_data.price = order.price

            # Add the instance to the combined_location list
            sales_data.save()
            combined_location.append(sales_data)

        # Iterate through CsvData
        for data in csv_data:
            # For each CsvData entry, create a SalesForLocation instance
            sales_data = SalesForLocation()
            sales_data.date = f"{data.year}-{data.month}-{data.day}"  # Adjust date format
            sales_data.fabric = data.fabric
            sales_data.set_type = data.setType
            sales_data.location = data.location
            sales_data.price = data.price

            # Add the instance to the combined_location list
            sales_data.save()
            combined_location.append(sales_data)

        messages.success(request, 'Location data migrated successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')

    # Redirect to the view you want (adjust the name accordingly)
    return HttpResponseRedirect(reverse('fchub:fchub-data-model'))


def migrate_color_data(request):
    try:
        combined_color = []

        # Retrieve data from the SuccessfulOrder model
        successful_orders = SuccessfulOrder.objects.all()

        # Iterate through SuccessfulOrder data
        for order in successful_orders:
            # For each SuccessfulOrder, create a SalesForColor instance
            sales_data = SalesForColor()
            sales_data.location = order.location
            sales_data.color = order.color
            sales_data.date = order.date
            sales_data.price = order.price

            # Add the instance to the combined_color list
            sales_data.save()
            combined_color.append(sales_data)

        messages.success(request, 'Color data migrated successfully.')
    except Exception as e:
        messages.error(request, f'Error: {e}')

    # Redirect to the view you want (adjust the name accordingly)
    return HttpResponseRedirect(reverse('fchub:fchub-data-model'))