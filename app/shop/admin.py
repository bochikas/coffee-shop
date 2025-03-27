from django.contrib import admin

from shop.models import Cart, Category, Order, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Категория."""


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Товар."""


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Корзина."""


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Заказ."""
