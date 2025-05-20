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
from django.urls import path
from app.views import ImportItemView, RegisterView, LoginView, ConfirmEmailView

urlpatterns = [
    path("api/v1/admin/", admin.site.urls),
    path("api/v1/import/", ImportItemView.as_view(), name="import-item"),
    path("api/v1/users/register/", RegisterView.as_view(), name="register"),
    path("api/v1/users/login/", LoginView.as_view(), name="login"),
    path("api/v1/users/confirm-email/", ConfirmEmailView.as_view(), name="confirm-email"),
]
