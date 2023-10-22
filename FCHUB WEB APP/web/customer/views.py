from collections import defaultdict
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
import requests
from .forms import CustomerEditForm, SignupForm, AddressEditForm ,CartForm, CartItemForm, OrderForm, PaymentForm, UserEditForm
from .models import Cart, CartItem, Customer, Order, Payment
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext as _
from .models import Customer, Product, User, Address
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from django.forms import formset_factory, modelformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Product  # Import your Product model
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Customer, Address, Product
from django.contrib.auth.models import User
from datetime import datetime  # Import datetime module
# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()

            # Retrieve address components
            region = form.cleaned_data['region']
            province = form.cleaned_data['province']
            city = form.cleaned_data['city']
            barangay = form.cleaned_data['barangay']
            street = form.cleaned_data['street']
            detailed_address = form.cleaned_data.get('detailed_address', '')  # Provide a default value if not present
            zipcode = form.cleaned_data.get('zipcode', '')  # Provide a default value if not present

            # Create the Customer object
            customer = Customer(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                gender=form.cleaned_data['gender'],
                profile_pic=form.cleaned_data.get('profile_pic', None)
            )
            customer.save()

            # Create the Address object
            address, created = Address.objects.get_or_create(
                region=region,
                province=province,
                city=city,
                barangay=barangay,
                street=street,
                detailed_address=detailed_address,
                zipcode=zipcode,
                customer=customer  # Associate the Address with the Customer instance
            )
            address.save()

            login(request, user)  # Log the user in after registration
            return redirect('/customer/home')  # Redirect to your desired page after successful registration
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})




class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'
    
    def form_invalid(self, form):
        messages.error(self.request, _('Invalid username or password'))  # Add a custom error message
        return super().form_invalid(form)

def customer_logout(request):
    logout(request)
    # You can add a custom message or additional logic here if needed.
    return redirect('customer:login')  # Redirect to the login page after logout

@login_required
def customer_home_view(request):
    customer = request.user.customer
    products = Product.objects.all()
    return render(request, 'customer/home.html', {'customer': customer, 'Products': products})

def access_denied(request):
    if isinstance(request.user, AnonymousUser):
        return render(request, 'access-denied.html')
    else:
        return redirect('customer:home')

@login_required
def profile(request):
    # Get the user's customer profile
    customer_profile = Customer.objects.get(user=request.user)
    
    # Get addresses associated with the customer
    customer_addresses = Address.objects.filter(customer=customer_profile)
    
    # Assuming you have a way to retrieve orders for the customer, replace this line with your logic
    # orders = Order.objects.filter(customer=customer_profile)

    return render(request, 'customer/profile.html', {
        'customer_profile': customer_profile,
        'customer_addresses': customer_addresses,
        # 'orders': orders,
    })

@login_required
def edit_profile(request):
    user = request.user
    customer = user.customer  # Assuming you have a one-to-one relationship with Customer

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        customer_form = CustomerEditForm(request.POST, instance=customer)
        address_form = AddressEditForm(request.POST, instance=customer.address)

        if user_form.is_valid() and customer_form.is_valid() and address_form.is_valid():
            user_form.save()
            customer_form.save()
            address_form.save()
            return redirect('profile')  # Redirect to the profile page or any other page
    else:
        user_form = UserEditForm(instance=user)
        customer_form = CustomerEditForm(instance=customer)
        address_form = AddressEditForm(instance=customer.address)

    print(user_form)
    print("hello there")

    return render(request, 'customer/edit-profile.html', {
        'user_form': user_form,
        'customer_form': customer_form,
        'address_form': address_form,
    })
# Cart Management Views
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(cart__customer=request.user.customer)
    total = 0  # Initialize total to zero
    quantity = 0  # Initialize quantity to zero

    for cart_item in cart_items:
        total += cart_item.product.price
        quantity += cart_item.quantity  # Added quantity

    return render(request, 'process/cart.html', {'cart_items': cart_items, 'total': total, 'quantity': quantity})  # Added quantity to the context dictionary

@login_required
def add_to_cart_view(request, pk):
    # Retrieve the product
    product = Product.objects.get(id=pk)
    # Get the customer's cart
    cart, created = Cart.objects.get_or_create(customer=request.user.customer)
    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    # If the item was created, set its quantity to 1, else, increment the quantity
    if created:
        cart_item.quantity = 1
    else:
        cart_item.quantity += 1
    cart_item.save()
    # Inform the user that the product has been added to the cart
    messages.info(request, f'{product.name} added to the cart successfully!')

    return HttpResponseRedirect(reverse('customer:home'))

@login_required
def remove_from_cart_view(request, pk):
    # Retrieve the product
    product = Product.objects.get(id=pk)

    # Get the customer's cart
    cart, created = Cart.objects.get_or_create(customer=request.user.customer)

    # Check if the product is in the cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

        # Inform the user that the product has been removed from the cart
        messages.info(request, f'{product.name} removed from the cart.')
    except CartItem.DoesNotExist:
        pass

    return HttpResponseRedirect(reverse('customer:cart'))

@login_required
def clear_cart_view(request):
    # Get the customer's cart
    cart, created = Cart.objects.get_or_create(customer=request.user.customer)

    # Clear all items from the cart
    cart_items = CartItem.objects.filter(cart=cart)
    cart_items.delete()

    # Inform the user that the cart has been cleared
    messages.info(request, 'Cart has been cleared successfully!')

    return HttpResponseRedirect(reverse('customer:cart'))

@login_required
def delete_from_cart_view(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)

    # Check if the cart item belongs to the current user
    if cart_item.cart.customer.user != request.user:
        # You might want to handle this case differently, e.g., return an error page
        return redirect('cart')  # Redirect back to the cart page

    # Delete the cart item
    cart_item.delete()

    return redirect('cart')  # Redirect back to the cart page

@login_required
def increase_quantity_view(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)

    # Increase the quantity by 1
    cart_item.quantity += 1
    cart_item.save()

    # Calculate the new total for this item
    item_total = cart_item.product.price * cart_item.quantity

    # Calculate the new cart total
    cart = cart_item.cart
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.product.price * item.quantity for item in cart_items)

    return JsonResponse({'new_quantity': cart_item.quantity, 'new_item_total': item_total, 'new_cart_total': total})

@login_required
def decrease_quantity_view(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)

    # Decrease the quantity by 1, but not below 1
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    # Calculate the new total for this item
    item_total = cart_item.product.price * cart_item.quantity

    # Calculate the new cart total
    cart = cart_item.cart
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.product.price * item.quantity for item in cart_items)

    return JsonResponse({'new_quantity': cart_item.quantity, 'new_item_total': item_total, 'new_cart_total': total})


@login_required
def proceed_purchase_view(request):
    user = request.user
    customer = get_object_or_404(Customer, user=user)
    customer_address = get_object_or_404(Address, customer=customer)

    # Fetch the items in the cart
    cart_items = CartItem.objects.filter(cart__customer=customer)

    # Calculate the total price and quantity
    total = sum(cart_item.product.price for cart_item in cart_items)
    quantity = sum(cart_item.quantity for cart_item in cart_items)  # Calculate total quantity

    # Calculate VAT and total with VAT
    vat_rate = Decimal('0.12')
    vat = total * vat_rate
    with_vat = total + vat

    # Determine shipping fee based on the region
    f_region = customer_address.region
    shipping_fee = 0
    total_price = 0

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
        shipping_fee = Decimal('500.00')

    total_price = with_vat + shipping_fee

    return render(request, 'process/proceed-purchase.html', {
        'shipping_fee': shipping_fee,
        'total_price': total_price,
        'vat': vat,
        'with_vat': with_vat,
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,  # Include quantity in the context
        'user': user,
        'customer': customer,
        'customer_address': customer_address,
    })




@login_required
def online_payment_view(request):
     # Your PayMongo API key (replace with your actual API key)
    api_key = "Basic c2tfdGVzdF85b3ltdlhraDhncnBwWmpHQnhYeFpjVFU6QEZsZWVreWh1Yb2tl1jkjd"

    user = User.objects.get(id=request.user.id)
    customer = get_object_or_404(Customer, user=user)
    customer_address = get_object_or_404(Address, customer=customer)
    cart = get_object_or_404(Cart, customer=customer)
    
    # Check if there are products in the cart
    product_ids = request.COOKIES.get('product_ids', '')
    product_id_in_cart = product_ids.split('|') if product_ids else []
    product_count_in_cart = len(set(product_id_in_cart))
    product_in_cart = product_count_in_cart > 0
    
    # Fetch product details from the database based on the IDs in the cookie
    products = Product.objects.filter(id__in=product_id_in_cart)

    # Calculate the total price and quantity based on products in the cart
    total = Decimal('0')
    quantity = 0  # Initialize quantity
    vat_rate = Decimal('0.12')  # 12% VAT rate

    for product in products:
        total += product.price
        quantity += 1  # Increment quantity for each product in the cart

    # Calculate VAT and total with VAT
    vat = total * vat_rate
    with_vat = total + vat

    # Determine shipping fee based on the region
    f_region = customer_address.region
    shipping_fee = 0

    regions_three = ["National Capital Region (NCR)", "Region I (Ilocos Region)", "Region II (Cagayan Valley)",
                     "Region III (Central Luzon)", "Region IV-A (CALABARZON)", "Region V (Bicol Region)"]
    regions_four = ["Region VI (Western Visayas)", "Region VII (Central Visayas)", "Region VIII (Eastern Visayas)"]
    regions_five = ["Region IX (Zamboanga Peninzula)", "Region X (Northern Mindanao)",
                    "Region XI (Davao Region)", "Region XII (SOCCSKSARGEN)", "Region XIII (Caraga)",
                    "Cordillera Administrative Region (CAR)", "Autonomous Region in Muslim Mindanao (ARMM)"]

    if f_region in regions_three:
        shipping_fee = Decimal('300')
    elif f_region in regions_four:
        shipping_fee = Decimal('400')
    elif f_region in regions_five:
        shipping_fee = Decimal('500.00')
        
    # Prepare line items for all products in the cart
    line_items = []
    for product in products:
        line_item = {
            "currency": "PHP",
            "amount": int((product.price * Decimal('100')).to_integral_value()),  # Convert price to cents
            "description": product.description,
            "name": product.name,
            "quantity": 1  # Each product is listed separately with quantity 1
        }
        line_items.append(line_item)

    # Add a line item for the shipping fee
    shipping_line_item = {
        "currency": "PHP",
        "amount": int((shipping_fee * Decimal('100')).to_integral_value()),  # Convert shipping fee to cents
        "description": f"Shipping Fee ({f_region})",
        "name": "Shipping",
        "quantity": 1
    }

    # Add a line item for the VAT
    vat_line_item = {
        "currency": "PHP",
        "amount": int((vat * Decimal('100')).to_integral_value()),  # Convert VAT to cents
        "description": "VAT (12%)",
        "name": "VAT",
        "quantity": 1
    }

    line_items.append(shipping_line_item)
    line_items.append(vat_line_item)

    fname = f"{customer.first_name} {customer.last_name}"

    # Prepare the payload for PayMongo API
    payload = {
        "data": {
            "attributes": {
                "billing": {
                    "address": {
                        "city": customer_address.city,
                        "state": customer_address.region,
                        "postal_code": customer_address.zipcode,
                        "country": "PH",  # Philippines (ISO 3166-1 alpha-2 code)
                        "line1": customer_address.barangay
                    },
                    "name": fname,
                    "email": customer.email,
                    "phone": customer.phone_number
                },
                "send_email_receipt": False,  # Set to False
                "show_description": True,
                "show_line_items": True,
                "cancel_url": request.build_absolute_uri('/proceed-purchase/'), # Cancel URL
                "success_url": request.build_absolute_uri('/customer/home'), #Add Success URL
                "description": "Order Description",
                "line_items": line_items,
                "payment_method_types": ["gcash", "grab_pay", "paymaya"]  # Add payment method types
            }
        }
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": api_key
    }


    # API endpoint for payment creation
    url = "https://api.paymongo.com/v1/checkout_sessions"
    try:
        # Make a POST request to create the payment session
        response = requests.post(url, json=payload, headers=headers)
        
        
        # Check if the request was successful
        if response.status_code == 200:
            # Payment session created successfully, retrieve the session URL
            payment_session_data = response.json()
            checkout_url = payment_session_data.get("data", {}).get("attributes", {}).get("checkout_url")
            response = HttpResponseRedirect(checkout_url)

            order = Order.objects.create(
                status="Pending",
                customer=customer,
                email=user.email,
                address=customer_address,
                mobile_number=customer.phone_number,
                cart=cart,
                payment_status="Pending"
            )
        
            # Create OrderProduct instances for each product in the cart
            for cart_product in cart.cartproduct_set.all():
                Order.objects.create(order=order, product=cart_product.product, quantity=cart_product.quantity)



            #response.delete_cookie('product_ids')
            return response
            # Redirect the user to the checkout URL
            
        else:
            # Payment session creation failed
            error_message = response.json().get("errors", "Payment session creation failed")
            # Handle the error as needed, e.g., return an error response
            return JsonResponse({"error": error_message}, status=400)
    except requests.exceptions.RequestException as e:
        # Handle network or request-related errors
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def my_order_view(request):
    if request.user.is_authenticated:
        try:
            # Retrieve the customer object
            customer = Customer.objects.get(user=request.user)
            orders = Order.objects.filter(customer=customer)
            order_products = CartItem.objects.filter(order__in=orders)  # Get all order products for the customer's orders

            order_bundles = {}  # Dictionary to group products by order
           
            
            for order_product in order_products:
                order = order_product.order
                product = order_product.product

                if order.id not in order_bundles:
                    order_bundles[order.id] = {
                        'order': order,
                        'products': [],
                    }

                order_bundles[order.id]['products'].append(product)
                print(order_bundles)
            return render(request, 'customer/my-order.html', {'order_bundles': order_bundles.values(), 'customer': customer})

        except Customer.DoesNotExist:
            return HttpResponse("Customer not found")

    else:
        return HttpResponse("Please log in to view your orders")