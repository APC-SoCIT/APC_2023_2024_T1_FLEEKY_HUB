from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from fchub.models import Product


class Customer(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    email = models.EmailField()
    phone_number = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.OneToOneField('Address',on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_addresses')
    profile_pic = models.ImageField(
        upload_to='customers/static/customer_profile_pic',
        null=True,
        default='customers/profile_pic/customer_profile_pic/akbay.png'
    )
    custom_id = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Increased max_length

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.custom_id:
            self.custom_id = self.generate_custom_id()
        super().save(*args, **kwargs)

    def generate_custom_id(self):
        # Generate the custom ID based on your criteria and convert it to uppercase
        username_part = self.user.username[:2].upper()
        first_name_part = self.first_name[:3].upper()
        last_name_part = self.last_name[:2].upper()
        gender_part = str(self.gender)[:0].upper()
        id_part = str(self.id)
        return f"{username_part}{first_name_part}{last_name_part}{gender_part}{id_part}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the object first so it gets an id
        self.custom_id = self.generate_custom_id()
        super().save(update_fields=['custom_id'])  # Save again to update the custom_id   
        
        class Meta:
            verbose_name = "Customer"


class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='address_customers')
    region = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    barangay = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    detailed_address = models.CharField(max_length=250)
    zipcode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.detailed_address}, {self.barangay}, {self.city}, {self.province}, {self.region}, {self.zipcode}"

    class Meta:
        verbose_name = "Address"



class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    item = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return self.customer.user.username + "'s Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Order Confirmed', 'Order Confirmed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )

    PAYMENT_CHOICES = (
        ("Online", "Online"),
        ("COD", "COD"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    total_price = models.DecimalField(max_digits=30, decimal_places=2)
    order_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.order_number
    
    def generate_order_number(self):
        order_date = self.order_date.strftime('%Y%m%d')
        random_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        first_letter_payment = self.payment_method[0].upper()
        self.order_number = f'{order_date}-{first_letter_payment}{self.customer.user.id}-{random_string}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.generate_order_number()
        super().save(*args, **kwargs)


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"
    