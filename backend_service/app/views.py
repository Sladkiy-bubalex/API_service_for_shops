import json

from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView
)

from app.permissions import IsSelfOrAdmin, IsShopOwner, IsCategoryOwner, IsProductOwner
from app.renderers import UserJSONRenderer
from app.filters import ProductInfoFilter
from app.models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
    User,
)
from app.serializers import (
    LoginSerializer,
    RegisterUserSerializer,
    ConfirmEmailSerializer,
    UserSerializer,
    ShopSerializer,
    CategorySerializer,
    ProductInfoSerializer,
    ProductInfoUpdateDestroySerializer,
)


def check_password(password: str) -> None | JsonResponse:
    try:
        validate_password(password=password)
    except ValidationError as e:
        return JsonResponse({"Error": f"Ошибка проверки пароля: {e}"}, status=400)


class ImportItemView(APIView):
    """Класс для импорта товаров"""

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request):
        if request.user.type != 'shop':
            return JsonResponse({'Error': "Импорт доступен только для магазинов"}, status=403)

        json_file = request.FILES.get("file")
        if json_file:
            try:
                data = json.load(json_file)
            except Exception:
                return JsonResponse({"Error": "Неверный формат файла"}, status=400)
            
            with transaction.atomic():
                shop, _ = Shop.objects.get_or_create(name=data["shop"], user=request.user)
                categories = data.get("category")
                if categories is None:
                    return JsonResponse({"Error": "Отсутствуют категории"}, status=400)
                for category in categories:
                    category, _ = Category.objects.get_or_create(name=category["name"])
                    category.shops.add(shop.id)
                    category.save()
            
                items = data.get("item")
                if items is None:
                    return JsonResponse({"Error": "Отсутствуют товары"}, status=400)
                for item in items:
                    product, _ = Product.objects.get_or_create(name=item["name"], categories_id=item["category"])
                    product_info, _ = ProductInfo.objects.get_or_create(
                        product_id=product.id,
                        shop_id=shop.id,
                        price=item["price"],
                        price_rrc=item["price_rrc"],
                        quantity=item["quantity"]
                        )

                parameters = item.get("parameters")
                if parameters is None:
                    return JsonResponse({"Error": "Отсутствуют параметры товара"}, status=400)
                for name, value in parameters.items():
                    parameter, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.get_or_create(
                        product_info_id=product_info.id,
                        parameter_id=parameter.id,
                        value=value
                    )

            return JsonResponse({"message": "Успешно"}, status=200)
        else:
            return JsonResponse({"Error": "Файл не загружен"}, status=400)


class RegisterView(CreateAPIView):
    """Класс для регистрации пользователя"""

    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
    def post(self, request: Request):
        # Проверка пароля.
        check_password(request.data["password"])

        # Проверка входящих данных и последующее сохрание в БД.
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data["email"],
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
                type=serializer.validated_data.get("type", "buyer"),
                company=serializer.validated_data.get("company", ""),
                position=serializer.validated_data.get("position", "")
            )
            return JsonResponse({"id": user.id, "message": "Вы успешно зарегистрированы!"}, status=201)

        return JsonResponse({"Errors": serializer.errors}, status=400)


class ConfirmEmailView(CreateAPIView):
    """Класс для подтверждения Email"""
    
    serializer_class = ConfirmEmailSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return JsonResponse({"message": "Email подтвержден!"}, status=200)

class LoginView(CreateAPIView):
    """Класс для авторизации пользователя"""
    
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
    def post(self, request: Request):
        # Проверка пароля.
        check_password(request.data["user"]["password"])

        user = request.data.get("user", {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return JsonResponse(serializer.data, status=200)


class UserListView(ListAPIView):
    """Класс для получения списка пользователей"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Если пользователь администратор, возвращаем всех пользователей
        if self.request.user.is_staff:
            return User.objects.all()
        # В противном случае возвращаем только текущего пользователя
        return User.objects.filter(id=self.request.user.id)


class UserDetailView(RetrieveUpdateDestroyAPIView):
    """Класс для получения, обновления и удаления пользователя"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    renderer_classes = (UserJSONRenderer,)
    permission_classes = (IsAuthenticated, IsSelfOrAdmin)


class ShopListView(ListAPIView):
    """Класс для получения списка магазинов"""
    
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)


class ShopDetailView(UpdateAPIView, DestroyAPIView):
    """Класс для обновления и удаления магазина"""
    
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated, IsShopOwner)


class CategoryListView(ListAPIView):
    """Класс для получения списка категорий"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class CategoryDetailView(UpdateAPIView, DestroyAPIView):
    """Класс для обновления и удаления категорий"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, IsCategoryOwner)


class ProductInfoListView(ListAPIView):
    """Класс для получения полного списка товаров со всеми параметрами"""
    
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductInfoFilter


class ProductInfoView(RetrieveAPIView):
    """Класс для получения полной информации о товаре"""
    
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    permission_classes = (IsAuthenticated,)

class ProductInfoDetailView(UpdateAPIView, DestroyAPIView):
    """Класс для обновления и удаления товара"""
    
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoUpdateDestroySerializer
    permission_classes = (IsAuthenticated, IsProductOwner)


