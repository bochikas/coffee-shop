from uuid import UUID

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1 import serializers
from api.v1.permissions import IsAdminOrReadOnly
from shop import models
from shop.tasks import send_order_notification

User = get_user_model()


class CheckUserActiveTokenRefreshView(TokenRefreshView):
    serializer_class = serializers.CheckUserActiveTokenRefreshSerializer


class CartView(APIView):
    """Корзина."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=serializers.CartSerializer)
    def get(self, request):
        cart = models.Cart.objects.select_related("user").prefetch_related("cartitem_set").get(user=request.user)
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

    def delete(self, request, item_id: UUID = None):
        cart = models.Cart.objects.get(user=request.user)
        if item_id:
            cart_item = get_object_or_404(models.CartItem, cart=cart, id=item_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            models.CartItem.objects.filter(cart=cart).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    """Заказы."""

    serializer_class = serializers.OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["user", "total_price", "created_at"]
    search_fields = ["user__username"]
    ordering_fields = ["total_price", "created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.Order.objects.none()
        if self.request.user.is_staff:
            return models.Order.objects.all()
        return models.Order.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in ("create", "retrieve", "list"):
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        cart = models.Cart.objects.filter(user=self.request.user).first()
        cart_items = models.CartItem.objects.filter(cart=cart).select_related("product")
        if not cart or not cart_items:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        order = models.Order.objects.create(user=self.request.user, total_price=total_price)

        for cart_item in cart_items:
            models.OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )

        models.CartItem.objects.filter(cart=cart).delete()
        send_order_notification.delay(order.id)

        headers = self.get_success_headers(serializers.OrderSerializer(order).data)
        return Response(serializers.OrderSerializer(order).data, status=status.HTTP_201_CREATED, headers=headers)


class UserVerificationView(generics.GenericAPIView):
    """Верификация пользователя."""

    permission_classes = [permissions.IsAdminUser]
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
    permission_classes = [IsAdminOrReadOnly]


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователя."""

    queryset = User.objects.all()
    serializer_class = serializers.UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class CategoryViewSet(viewsets.ModelViewSet):
    """Категории."""

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title"]


class ProductViewSet(viewsets.ModelViewSet):
    """Продукты."""

    queryset = models.Product.objects.select_related("category").all()
    serializer_class = serializers.ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title"]


class ShopInfoView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = {
            "title": "Coffee to Go",
            "location": "111 Street, City",
            "working_hours": {
                "Monday-Friday": "7:00 AM - 20:00",
                "Saturday-Sunday": "9:00 AM - 19:00",
            },
            "contact": {
                "phone": "+99999999999",
                "email": "mail@example.com",
            },
        }
        return Response(data)
