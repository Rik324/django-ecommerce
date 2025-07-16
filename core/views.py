import random
import string

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
# 👇 1. ADD FormView to this import
from django.views.generic import ListView, DetailView, View, FormView

# 👇 2. IMPORT the new models and form for the quotation feature
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, QuotationRequestForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, QuotationRequest, QuotationRequestItem


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

# --- Your existing views are here (unchanged) ---

class CheckoutView(View):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here

class PaymentView(View):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here


@login_required
def remove_from_cart(request, slug):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here


@login_required
def remove_single_item_from_cart(request, slug):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here


def get_coupon(request, code):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here


class AddCouponView(View):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here


class RequestRefundView(View):
    # ... (your existing code) ...
    pass # I'm collapsing this for brevity, but your code is here

# ===================================================================
# == ✅ 3. ADD THE NEW QUOTATION VIEW AT THE END
# ===================================================================

class RequestQuoteView(LoginRequiredMixin, FormView):
    """
    This view handles displaying the form for a quotation request
    and processing the submitted data.
    """
    form_class = QuotationRequestForm
    template_name = 'request_quote.html' # We will create this HTML file next

    def get_item(self):
        """Helper method to get the item from the URL's slug."""
        slug = self.kwargs.get('slug')
        item = get_object_or_404(Item, slug=slug)
        return item

    def get_context_data(self, **kwargs):
        """Adds the item object to the template context."""
        context = super().get_context_data(**kwargs)
        context['item'] = self.get_item()
        return context

    def form_valid(self, form):
        """
        This method runs when the user submits a valid form. It saves
        the request to the database.
        """
        quantity = form.cleaned_data.get('quantity')
        user_notes = form.cleaned_data.get('user_notes')
        item = self.get_item()
        
        # Create the main QuotationRequest object
        quote_request = QuotationRequest.objects.create(
            user=self.request.user,
            user_notes=user_notes
        )
        
        # Create the specific item linked to that request
        QuotationRequestItem.objects.create(
            quotation_request=quote_request,
            item=item,
            quantity=quantity
        )
        
        messages.success(self.request, "Your quotation request has been submitted successfully!")
        
        # Redirect the user back to the product page
        return redirect("core:product", slug=item.slug)
    # ... your other views and imports are at the top ...


# ===================================================================
# == ✅ NEW "MY QUOTES" VIEW
# ===================================================================

class MyQuotesView(LoginRequiredMixin, ListView):
    """
    This view displays a list of all quotation requests submitted
    by the currently logged-in user.
    """
    model = QuotationRequest
    template_name = 'my_quotes.html'  # The HTML file we will create next
    context_object_name = 'quotes'     # The name for the list of quotes in the template
    paginate_by = 10                   # Optional: Show 10 quotes per page

    def get_queryset(self):
        """
        This method ensures that users can only see their own quotes,
        not quotes from other users.
        """
        # Filter the quotation requests by the current user and order by most recent
        return QuotationRequest.objects.filter(user=self.request.user).order_by('-created_at')