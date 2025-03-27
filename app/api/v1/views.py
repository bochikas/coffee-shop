from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1 import serializers
from shop import models

User = get_user_model()


class CheckUserActiveTokenRefreshView(TokenRefreshView):
    serializer_class = serializers.CheckUserActiveTokenRefreshSerializer


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя."""

    queryset = User.objects.all()
    serializer_class = serializers.UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserVerificationView(generics.GenericAPIView):
    """Верификация пользователя."""

    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.UserVerificationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get("username")

        if user := User.objects.filter(username=username).first():
            user.is_verified = True
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserInfoView(generics.RetrieveAPIView):
    """Информация о пользователе."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """Пользователи."""

    http_method_names = ["get", "put", "patch", "delete"]
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    """Категории."""

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    """Продукты."""

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = [permissions.AllowAny]


class CartView(APIView):
    """Корзина."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=serializers.CartSerializer)
    def get(self, request):
        cart = models.Cart.objects.get(user=request.user)
        serializer = serializers.CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=serializers.AddProductToCartSerializer, responses=serializers.CartSerializer)
    def post(self, request):
        serializer = serializers.AddProductToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.data.get("product")
        quantity = serializer.data.get("quantity")
        cart, _ = models.Cart.objects.get_or_create(user=request.user)
        cart_item, created = models.CartItem.objects.get_or_create(cart=cart, product_id=product)
        if created:
            cart_item.quantity = int(quantity)
        else:
            cart_item.quantity += int(quantity)
        cart_item.save()
        return Response(serializers.CartSerializer(cart).data, status=status.HTTP_200_OK)

    def delete(self, request, item_id=None):
        cart = models.Cart.objects.get(user=request.user)
        if item_id:
            cart_item = models.CartItem.objects.get(cart=cart, id=item_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            models.CartItem.objects.filter(cart=cart).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    """Заказы."""

    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
