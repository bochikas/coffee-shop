from django.contrib.auth import get_user_model
from django.db import models

from base.models import BaseModel, CreatedAtModel, IsActiveTitleTimeStampedModel

User = get_user_model()


class Category(IsActiveTitleTimeStampedModel):
    """Категория продукта."""

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.title


class Product(IsActiveTitleTimeStampedModel):
    """Товар."""

    description = models.TextField(blank=True, null=True, verbose_name="описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="цена")
    category = models.ForeignKey(Category, verbose_name="категория", on_delete=models.CASCADE, related_name="products")

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.title


class Cart(BaseModel):
    """Корзина."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь")
    products = models.ManyToManyField(Product, through="CartItem")

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "корзины"

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(BaseModel):
    """Товар в корзине."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="количество")

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


class OrderStatus(models.TextChoices):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class Order(CreatedAtModel):
    """Заказ."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="итоговая цена")
    status = models.CharField(
        max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING, verbose_name="статус"
    )

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

    def __str__(self):
        return f"Order {self.id} - {self.status}"
