from django.contrib import admin
from django.utils.html import format_html

from .models import Category, OrderRequest, Product, SiteSettings

admin.site.site_header = "Ira admin"
admin.site.site_title = "Ira admin"
admin.site.index_title = "Manage the shop"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["__str__", "store_name", "whatsapp_number", "phone_display"]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class ProductInline(admin.TabularInline):
    model = Product
    fields = ["name", "price", "sizes", "is_active", "sort_order"]
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "section", "sort_order", "product_count"]
    list_editable = ["sort_order"]
    list_filter = ["section"]
    inlines = [ProductInline]

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["thumbnail", "name", "category", "price", "sizes", "is_active", "sort_order"]
    list_display_links = ["thumbnail", "name"]
    list_editable = ["price", "is_active", "sort_order"]
    list_filter = ["category__section", "category", "is_active"]
    search_fields = ["name"]
    list_select_related = ["category"]
    readonly_fields = ["preview", "created_at", "updated_at"]
    fields = ["category", "name", "price", "sizes", "image", "preview", "is_active", "sort_order", "created_at", "updated_at"]

    @admin.display(description="")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px">', obj.image.url)
        return "-"

    @admin.display(description="Current image")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:200px;border-radius:8px">', obj.image.url)
        return "No image uploaded (a placeholder is shown on the site)."


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ["created_at", "product_name", "size", "price"]
    list_filter = ["created_at", "product__category__section"]
    search_fields = ["product_name"]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
