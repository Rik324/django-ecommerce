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
# 👇 Add TemplateView to this import
from django.views.generic import ListView, DetailView, View, FormView, TemplateView

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

class CheckoutView(View):
    # ... (your existing code) ...
    pass

class PaymentView(View):
    # ... (your existing code) ...
    pass

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    # ... (your existing code) ...
    pass

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    # ... (your existing code) ...
    pass

@login_required
def remove_from_cart(request, slug):
    # ... (your existing code) ...
    pass

@login_required
def remove_single_item_from_cart(request, slug):
    # ... (your existing code) ...
    pass

def get_coupon(request, code):
    # ... (your existing code) ...
    pass

class AddCouponView(View):
    # ... (your existing code) ...
    pass

class RequestRefundView(View):
    # ... (your existing code) ...
    pass

class RequestQuoteView(LoginRequiredMixin, FormView):
    form_class = QuotationRequestForm
    template_name = 'request_quote.html'

    def get_item(self):
        slug = self.kwargs.get('slug')
        item = get_object_or_404(Item, slug=slug)
        return item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.get_item()
        return context

    def form_valid(self, form):
        quantity = form.cleaned_data.get('quantity')
        user_notes = form.cleaned_data.get('user_notes')
        item = self.get_item()
        
        quote_request = QuotationRequest.objects.create(
            user=self.request.user,
            user_notes=user_notes
        )
        
        QuotationRequestItem.objects.create(
            quotation_request=quote_request,
            item=item,
            quantity=quantity
        )
        
        messages.success(self.request, "Your quotation request has been submitted successfully!")
        return redirect("core:product", slug=item.slug)

class MyQuotesView(LoginRequiredMixin, ListView):
    model = QuotationRequest
    template_name = 'my_quotes.html'
    context_object_name = 'quotes'
    paginate_by = 10

    def get_queryset(self):
        return QuotationRequest.objects.filter(user=self.request.user).order_by('-created_at')

class CategoryView(ListView):
    model = Item
    template_name = "category_page.html"
    context_object_name = 'items'
    paginate_by = 10

    CATEGORY_MAPPING = {
        'fruits': 'F',
        'vegetables': 'V',
        'thai-rice': 'TR',
        'thai-herbs': 'TH'
    }

    def get_queryset(self):
        self.category_slug = self.kwargs.get('category_slug')
        category_code = self.CATEGORY_MAPPING.get(self.category_slug)
        queryset = Item.objects.filter(category=category_code)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = self.category_slug.replace('-', ' ').title()
        return context

# ===================================================================
# == ✅ NEW ACCOUNT VIEW (ADDED CODE)
# ===================================================================

class AccountView(LoginRequiredMixin, TemplateView):
    """
    This view displays the user's account page with their profile
    and default address information.
    """
    template_name = "my_account.html"  # We will create this HTML file next

    def get_context_data(self, **kwargs):
        """
        This method fetches all the necessary information for the account page
        and sends it to the template.
        """
        context = super().get_context_data(**kwargs)
        
        # Get the current user's default shipping and billing addresses
        try:
            context['default_shipping_address'] = Address.objects.get(
                user=self.request.user, address_type='S', default=True)
        except Address.DoesNotExist:
            context['default_shipping_address'] = None

        try:
            context['default_billing_address'] = Address.objects.get(
                user=self.request.user, address_type='B', default=True)
        except Address.DoesNotExist:
            context['default_billing_address'] = None
            
        return context
    # ... all of your other views are above this ...


# ===================================================================
# == ✅ ADD THIS VIEW TO THE END OF YOUR FILE
# ===================================================================

class AcceptQuoteView(LoginRequiredMixin, View):
    """
    Handles the logic for when a user accepts a price quote.
    """
    def get(self, request, *args, **kwargs):
        quote_id = self.kwargs.get('quote_id')
        
        # Find the specific quote, ensuring it belongs to the current user
        # and is in the 'ANSWERED' state. This is a security measure.
        quote = get_object_or_404(
            QuotationRequest, 
            id=quote_id, 
            user=self.request.user, 
            status='ANSWERED'
        )

        # 1. Create a new Order based on the accepted quote
        new_order = Order.objects.create(
            user=self.request.user,
            ordered_date=timezone.now()
        )

        # 2. Copy each item from the quote to the new order
        order_items = []
        for quote_item in quote.items.all():
            order_item = OrderItem.objects.create(
                item=quote_item.item,
                user=self.request.user,
                quantity=quote_item.quantity
            )
            order_items.append(order_item)
        
        # Add all the newly created OrderItems to the Order
        new_order.items.add(*order_items)
        new_order.save()

        # 3. Update the quote's status to 'ACCEPTED' and link it to the new order
        quote.status = 'ACCEPTED'
        quote.order = new_order
        quote.save()
        
        # 4. Show a success message and redirect the user to their order summary (cart)
        messages.success(self.request, "Quote accepted! The items have been added to a new order in your cart.")
        return redirect("core:order-summary")