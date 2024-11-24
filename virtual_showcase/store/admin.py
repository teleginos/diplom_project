from django.contrib import admin
from .models import Product, Category,Subcategory, Order, OrderItem
from .forms import ProductAdminForm

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    list_display = ('name', 'category', 'subcategory', 'price')
    search_fields = ['name']

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 0

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [SubcategoryInline]

admin.site.register(Product, ProductAdmin)
# admin.site.register(Category)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)