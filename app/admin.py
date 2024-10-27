from django.contrib import admin
from .models import Farmer, Product,Message
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'quantity', 'price', 'expiry_date')  # Include 'farmer'
    list_filter = ('farmer', 'quality')  # Include 'farmer' for filtering

admin.site.register(Farmer)
admin.site.register(Message)  # Register Farmer model
admin.site.register(Product, ProductAdmin)