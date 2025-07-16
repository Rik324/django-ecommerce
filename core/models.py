# This file defines the structure of your application's database.
# Each class represents a database table.

from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

# ===================================================================
# == ORIGINAL E-COMMERCE MODELS
# ===================================================================

class UserProfile(models.Model):
    # This model adds extra information to the default Django User.
    # The OneToOneField ensures each user has only one profile.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE  # If the user is deleted, this profile is also deleted.
    )
    # These fields are for payment integration with Stripe.
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True) # Optional field
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        # This defines what name is shown in the Django admin panel.
        return self.user.username

class Item(models.Model):
    # This model represents a product you are selling.
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True) # Optional discount price.
    
    # Choices limit the options for the category field.
    CATEGORY_CHOICES = (
        ('F', 'Fruits'),
        ('V', 'Vegetables'),
        ('TR', 'Thai Rice'),
        ('TH', 'Thai Herbs')
    )
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    
    # Choices for product labels like 'New' or 'On Sale'.
    LABEL_CHOICES = (
        ('N', 'New'),
        ('B', 'Best Seller'),
        ('S', 'On Sale')
    )
    label = models.CharField(choices=LABEL_CHOICES, max_length=2)
    
    slug = models.SlugField() # A field for creating user-friendly URLs (e.g., /products/thai-rice).
    description = models.TextField()
    image = models.ImageField(upload_to='') # Field to upload a product image.

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    # This represents one item in a user's shopping cart (e.g., 3 apples).
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE) # The specific product.
    quantity = models.IntegerField(default=1) # How many of that product.
    ordered = models.BooleanField(default=False) # Becomes True when the user checks out.

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

class Order(models.Model):
    # This represents a completed order after checkout.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True) # A unique reference code for the order.
    
    # A ManyToManyField links this order to all its OrderItems.
    items = models.ManyToManyField(OrderItem)
    
    start_date = models.DateTimeField(auto_now_add=True) # Automatically sets the creation date.
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    
    # Links to the shipping and billing addresses for this order.
    # on_delete=models.SET_NULL means if the address is deleted, this field becomes empty (null).
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    
    # Boolean fields to track the order status.
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Address(models.Model):
    # Stores a user's address.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    
    # To specify if it's a billing or shipping address.
    ADDRESS_CHOICES = (
        ('B', 'Billing'),
        ('S', 'Shipping'),
    )
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False) # To mark one address as the default.

    def __str__(self):
        return self.user.username

    class Meta:
        # This makes sure the plural form is "Addresses" in the admin panel.
        verbose_name_plural = 'Addresses'

class Payment(models.Model):
    # Records a payment transaction.
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username if self.user else self.stripe_charge_id

class Coupon(models.Model):
    # Stores a discount coupon.
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code

class Refund(models.Model):
    # Manages a refund request for an order.
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"Refund for order #{self.order.id}"

# ===================================================================
# == ✅ NEW 'REQUEST QUOTATION' MODELS
# ===================================================================

class QuotationRequest(models.Model):
    """
    This model stores a user's request for a price quote. It's separate
    from the main shopping cart and order system.
    """
    STATUS_CHOICES = (
        ('SUBMITTED', 'Submitted'), # User sent the request
        ('ANSWERED', 'Answered'),   # Admin provided a quote
        ('ACCEPTED', 'Accepted'),   # User accepted the quote
        ('REJECTED', 'Rejected'),   # User rejected the quote
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SUBMITTED')
    user_notes = models.TextField(blank=True, null=True, help_text="Any details from the user.")
    admin_notes = models.TextField(blank=True, null=True, help_text="Notes from the admin about the quote.")
    proposed_total = models.FloatField(blank=True, null=True, help_text="The price quoted by the admin.")
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(blank=True, null=True)
    
    # This field can link an accepted quote to a real order for payment.
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Quote #{self.id} for {self.user.username} ({self.status})"

    class Meta:
        ordering = ['-created_at'] # Shows newest quotes first.


class QuotationRequestItem(models.Model):
    """
    This stores a single item inside a quotation request (e.g., 100 apples).
    """
    # Links this item back to its main quotation request.
    # The 'related_name' lets us easily get all items from a quote object.
    quotation_request = models.ForeignKey(QuotationRequest, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) # Ensures quantity is not negative.

    def __str__(self):
        return f"{self.quantity} of {self.item.title} for Quote #{self.quotation_request.id}"