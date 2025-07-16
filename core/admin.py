from django.contrib import admin
from .models import (
    Item, 
    OrderItem, 
    Order, 
    Payment, 
    Coupon, 
    Refund, 
    Address, 
    UserProfile,
    Post,
    QuotationRequest,
    QuotationRequestItem
)

# This is a custom action for the Order model in the admin panel.
def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)
make_refund_accepted.short_description = 'Update order to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted'
                    ]
    list_display_links = ['user']
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = ['user__username', 'ref_code']
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


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'price',
        'discount_price',
        'category',
        'label',
    ]
    list_filter = ['category', 'label']
    search_fields = ['title', 'description']


class QuotationRequestItemInline(admin.TabularInline):
    """Allows you to see items within a quote request."""
    model = QuotationRequestItem
    extra = 0


class QuotationRequestAdmin(admin.ModelAdmin):
    """Customizes the admin for Quotation Requests."""
    inlines = [QuotationRequestItemInline]
    list_display = ('id', 'user', 'status', 'created_at', 'proposed_total')
    list_filter = ('status',)
    search_fields = ('user__username',)
    list_display_links = ('id', 'user')
    list_editable = ('status', 'proposed_total')


class PostAdmin(admin.ModelAdmin):
    """Customizes the admin for Blog Posts."""
    list_display = ('title', 'slug', 'status', 'created_at')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


# Register all your models with the admin site
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(QuotationRequest, QuotationRequestAdmin)
admin.site.register(Post, PostAdmin)

# These models don't need special admin classes, so we register them simply
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(UserProfile)