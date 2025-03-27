from dj_rest_auth.views import LoginView
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

from api.v1 import views

router = routers.DefaultRouter()

router.register("users", views.UserViewSet, basename="users")
router.register("category", views.CategoryViewSet, basename="category")
router.register("products", views.ProductViewSet, basename="products")
router.register("orders", views.OrderViewSet, basename="orders")

urlpatterns = [
    # YOUR PATTERNS
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("auth/authentication/", LoginView.as_view(), name="rest_login"),
    path("auth/verification/", views.UserVerificationView.as_view(), name="rest_verification"),
    path("auth/registration/", views.UserRegistrationView.as_view(), name="rest_registration"),
    path("users/me/", views.UserInfoView.as_view(), name="rest_user_details"),
    path("token/refresh/", views.CheckUserActiveTokenRefreshView.as_view(), name="rest_token_refresh"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/<uuid:item_id>/", views.CartView.as_view(http_method_names=["delete"]), name="cart-item-delete"),
    path("", include(router.urls)),
]
