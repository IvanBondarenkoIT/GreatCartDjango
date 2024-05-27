from django.contrib import admin
from store.models import Product, Variations, ProductGallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


@admin_thumbnails.thumbnail('image')
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]


class VariationsAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_active', 'variation_category', 'variation_value', 'created_date')
    list_editable = ('is_active', )
    list_filter = ('product', 'variation_category', 'variation_value')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variations, VariationsAdmin)
admin.site.register(ProductGallery)
