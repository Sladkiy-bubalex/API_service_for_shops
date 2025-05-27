"""
URL configuration for backend_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views import (
    ImportItemView, RegisterView, LoginView, ConfirmEmailView,
    UserDetailView, UserListView,
    CategoryListView, CategoryDetailView,
    ShopListView, ShopDetailView,
    PartnerProductInfoViewSet, ProductInfoListView, ProductInfoView,
    BasketListView,
    ContactViewSet,
    OrderView,
)

router = DefaultRouter()
router.register("contacts", ContactViewSet, basename="contacts")
router.register("products/partner", PartnerProductInfoViewSet, basename="products-partner")

urlpatterns = [
    path("api/v1/admin/", admin.site.urls),
    path("api/v1/import/", ImportItemView.as_view(), name="import-item"),

    path("api/v1/users/", UserListView.as_view(), name="users"),
    path("api/v1/users/register/", RegisterView.as_view(), name="register"),
    path("api/v1/users/login/", LoginView.as_view(), name="login"),
    path("api/v1/users/confirm-email/", ConfirmEmailView.as_view(), name="confirm-email"),
    path("api/v1/users/<int:pk>", UserDetailView.as_view(), name="user"),

    path("api/v1/categories/", CategoryListView.as_view(), name="categories"),
    path("api/v1/categories/<int:pk>", CategoryDetailView.as_view(), name="category"),

    path("api/v1/shops/", ShopListView.as_view(), name="shops"),
    path("api/v1/shops/<int:pk>", ShopDetailView.as_view(), name="shop"),

    path("api/v1/products/", ProductInfoListView.as_view(), name="products"),
    path("api/v1/products/<int:pk>", ProductInfoView.as_view(), name="product"),

    path("api/v1/basket/", BasketListView.as_view(), name="basket"),

    path("api/v1/orders/", OrderView.as_view(), name="orders"),

    path("api/v1/", include(router.urls)),
]
