from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from shop.models import Cart, CartItem, Category, Order, OrderItem, Product

User = get_user_model()


class NoEmailLoginSerializer(LoginSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("email", None)


class CheckUserActiveTokenRefreshSerializer(TokenRefreshSerializer):
    """Сериализатор обновления токена с проверкой активности пользователя."""

    def validate(self, attrs):
        data = super().validate(attrs)
        # Получаем пользователя из токена
        refresh = RefreshToken(data["refresh"])
        user_id = refresh["user_id"]
        try:
            user = User.objects.get(id=user_id)
            if not user.is_active or not user.is_verified:
                refresh.blacklist()
                raise serializers.ValidationError({"error": "User account is inactive."})
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found."})

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_verified"]


class UserVerificationSerializer(serializers.ModelSerializer):
    """Сериализатор верификации пользователя."""

    class Meta:
        model = User
        fields = ["id", "username"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя."""

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password2"]

    def validate(self, data):
        validate_data = super().validate(data)

        if validate_data["password"] != validate_data.pop("password2"):
            raise serializers.ValidationError("Passwords don't match")
        return validate_data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий."""

    class Meta:
        model = Category
        fields = ("id", "title")


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор товара."""

    class Meta:
        model = Product
        fields = ("id", "title", "description", "price", "category")


class AddProductToCartSerializer(serializers.ModelSerializer):
    """Сериализатор добавления товара в корзину."""

    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity")


class CartItemSerializer(serializers.ModelSerializer):
    """Сериализатор товара корзины."""

    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity")


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    items = CartItemSerializer(many=True, read_only=True, source="cartitem_set")

    class Meta:
        model = Cart
        fields = ("id", "user", "items")


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор позиции заказа."""

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "price")


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор заказа."""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "user", "total_price", "created_at", "status", "items")
        read_only_fields = ("created_at", "status")
