from django.contrib import admin
from .models import UserActivity, UserProfile, Product, CartItem, Order, Receipt

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('timestamp',)

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Receipt)
