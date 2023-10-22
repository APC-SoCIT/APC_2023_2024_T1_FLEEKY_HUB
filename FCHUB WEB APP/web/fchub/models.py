from django.db import models
from django.contrib.auth.models import User
from django.utils.dates import MONTHS


class FleekyAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField('First Name', max_length=50)
    last_name = models.CharField('Last Name', max_length=50)
    login_time = models.DateTimeField(null=True, blank=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Admin"


class Category(models.Model):
    FABRIC_CHOICES = (
        ('Katrina', 'Katrina'),
        ('Blockout', 'Blockout'),
        ('Sheer', 'Sheer'),
        ('Korean', 'Korean'),
    )
    
    SET_TYPE_CHOICES = (
        ('Singles', 'Singles'),
        ('3 in 1', '3 in 1'),
        ('4 in 1', '4 in 1'),
        ('5 in 1', '5 in 1'),
    )

    fabric = models.CharField(max_length=250, choices=FABRIC_CHOICES)
    setType = models.CharField(max_length=250, choices=SET_TYPE_CHOICES)
    description = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.fabric} - {self.setType}"
    
    @property
    def custom_category_id(self):
        fabric_short = self.fabric[:2]  # First two letters of fabric
        set_type_short = self.setType.replace(" ", "").replace("in", "")[:3]  # First three letters of set type
        return f"{fabric_short}{set_type_short}{self.id}"
    
class Product(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_image = models.ImageField(upload_to='customers/static/product_images', null=True, blank=True)
    stock = models.PositiveIntegerField()
    color = models.CharField(max_length=100)
    custom_id = models.CharField(max_length=20, unique=True, blank=True, null=True) 
    def __str__(self):
        return self.name
    
    #SKU
    @property
    def custom_product_id(self):
        # Generate the custom product ID based on category ID, first three letters of color, and ID
        category_id = self.category_id  # Assumes you have a category_id field in the Category model
        color_short = self.color[:3]  # First three letters of color
        return f"{category_id}{color_short}{self.id}"
    
    def save(self, *args, **kwargs):
        # Generate and set the custom product ID before saving the object
        self.custom_id = self.custom_product_id
        super(Product, self).save(*args, **kwargs)

class Material(models.Model):
    name = models.CharField(max_length=250)
    qty = models.CharField(max_length=250)
    unit = models.CharField(max_length=250)
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=250,null=True)
    def __str__(self):
        return self.name
    
class analytics(models.Model):
    
    PAYMENT_CHOICES = (
        ('GCASH','GCASH'),
        ('CASH ON DELIVERY','CASH ON DELIVERY'),
        ('LBC','LBC'),
        ('OTHERS','OTHERS'),
    )
    PRODUCT_TAG_CHOICES = (
        (1, 'Blockout'),
        (2, '5-in-1 Katrina'),
        (3, '3-in-1 Katrina'),
        (4, 'Tieback Holder'),
    )
    FABRIC_CHOICES = (
        ('Katrina','Katrina'),
        ('Blockout','Blockout'),
        ('Sheer','Sheer'),
        ('None','None'),
    )
    
    SET_CHOICES = (
        ('5-in-1','5-in-1'),
        ('3-in-1','3-in-1'),
        ('Single','Single'),
        ('None','None'),
    )
    fabric_type = models.CharField(max_length=250, null= True,choices=FABRIC_CHOICES)
    payment = models.CharField(max_length=250,null=True,choices=PAYMENT_CHOICES)
    price  = models.PositiveIntegerField(null=True)
    color = models.CharField(max_length=250, null=True)
    product_tag = models.SmallIntegerField(choices=PRODUCT_TAG_CHOICES)
    set_tag = models.CharField(max_length=250, choices=SET_CHOICES, null=True)
    month_of_purhase = models.PositiveSmallIntegerField(null=True,choices=MONTHS.items())
    qty = models.PositiveIntegerField(null=True)
    count = models.PositiveIntegerField(null=True)
