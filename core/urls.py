from django.urls import path
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    RequestQuoteView,
    MyQuotesView,
    CategoryView,
    AccountView,
    AcceptQuoteView, # 👈 1. Import the new view
    SearchResultsView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('request-quote/<slug>/', RequestQuoteView.as_view(), name='request-quote'),
    path('my-quotes/', MyQuotesView.as_view(), name='my-quotes'),
    path('category/<slug:category_slug>/', CategoryView.as_view(), name='category_view'),
    path('my-account/', AccountView.as_view(), name='my-account'),

    # 👇 2. Add this new URL for accepting a quote
    path('accept-quote/<int:quote_id>/', AcceptQuoteView.as_view(), name='accept-quote'),

    path('search/', SearchResultsView.as_view(), name='search_results'),
]