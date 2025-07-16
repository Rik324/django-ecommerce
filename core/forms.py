# This file defines all the forms used across your e-commerce site.

from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Refund  # We need to import the Refund model for our new RefundForm

# ===================================================================
# == E-COMMERCE FORMS
# ===================================================================

class CheckoutForm(forms.Form):
    """
    This form collects all the necessary information during the checkout process,
    like shipping and billing addresses.
    """
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    # This is the modern way to create a country selection field
    shipping_country = CountryField().formfield(
        required=False,
        widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'})
    )
    shipping_zip = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField().formfield(
        required=False,
        widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'})
    )
    billing_zip = forms.CharField(required=False)

    # These boolean fields (checkboxes) are used to control logic in your view
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    # This creates the payment option choices (e.g., Stripe or PayPal)
    PAYMENT_CHOICES = (
        ('S', 'Stripe'),
        ('P', 'PayPal')
    )
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    """A simple form for a user to enter a coupon code."""
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.ModelForm):
    """
    Handles refund requests.
    
    IMPROVEMENT: We changed this from a standard Form to a ModelForm.
    A ModelForm automatically builds a form from your model, which saves time
    and is less error-prone.
    """
    # This field is NOT in the Refund model, but we need it on the form so the
    # user can tell us which order they want to refund.
    ref_code = forms.CharField(label="Your Order Reference Code")

    class Meta:
        model = Refund  # Link this form directly to the Refund model
        # Specify which fields from the model should appear on the form
        fields = ['reason', 'email']
        # Customize the labels and input types for the fields
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please tell us why you need a refund.'}),
        }
        labels = {
            'reason': 'Message' # Change the display label for the 'reason' field
        }


class PaymentForm(forms.Form):
    """
    This form is used on the payment page to handle data from Stripe
    and user choices for saving payment info.
    """
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


# ===================================================================
# == ✅ NEW QUOTATION FORM
# ===================================================================

class QuotationRequestForm(forms.Form):
    """
    This is the new form for a user to request a price quote for an item.
    """
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    user_notes = forms.CharField(
        required=False,
        label="Notes or Questions",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'e.g., I would like to inquire about bulk pricing...'
        })
    )