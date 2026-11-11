from django.contrib import admin
from django.db.models import Count

from .models import Category, Product, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=["name","parent","product_count"]
    list_filter= ["parent"]
    search_fields  = ["name"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_products = Count("products"))

    @admin.display(description="Products", ordering="num_products")
    def product_count(self, obj):
        return obj.num_products 

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "product_count"]
    search_fields = ["name"]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_products=Count("products"))

    @admin.display(description="Products", ordering="num_products")
    def product_count(self, obj):
        return obj.num_products


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "created_at"]
    list_filter = ["category", "tags"]
    search_fields = ["name", "description"]
    filter_horizontal = ["tags"]
    list_select_related = ["category"]