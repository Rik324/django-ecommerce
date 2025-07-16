from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update order to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user__username', 'street_address', 'apartment_address', 'zip']


class ItemAdmin(admin.ModelAdmin): # Add or modify this class
    list_display = [
        'title',
        'price',
        'discount_price',
        'category',
        'label',
    ]
    list_filter = ['category', 'label'] # Add new fields to filter
    search_fields = ['title', 'description']


admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
from django.contrib import admin
from .models import (
    # ... your other models might be registered here ...
    QuotationRequest,
    QuotationRequestItem
)

class QuotationRequestItemInline(admin.TabularInline):
    """
    This allows you to see and edit the items directly within
    the Quotation Request page in the admin panel.
    """
    model = QuotationRequestItem
    extra = 0 # Don't show any extra empty forms by default


class QuotationRequestAdmin(admin.ModelAdmin):
    """
    This customizes how the list of quotation requests is displayed.
    """
    # This shows the items right on the quotation request page.
    inlines = [QuotationRequestItemInline]

    # These are the fields you will see in the list of all quotes.
    list_display = (
        'id',
        'user',
        'status',
        'created_at',
        'proposed_total'
    )

    # This adds a filter sidebar to filter by status.
    list_filter = ('status',)

    # This adds a search bar to search by user's username.
    search_fields = ('user__username',)

    # This makes these fields clickable links in the admin list.
    list_display_links = ('id', 'user')

    # You can't edit these fields directly in the list view.
    list_editable = ('status', 'proposed_total')


# Register your models with the admin site
admin.site.register(QuotationRequest, QuotationRequestAdmin)
# We don't need a separate admin page for QuotationRequestItem,
# as it's handled by the inline view above.