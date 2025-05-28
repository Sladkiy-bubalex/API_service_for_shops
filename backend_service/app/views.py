import json

from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse, Http404
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, F
from django.db import transaction, IntegrityError

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    ListCreateAPIView
)

from app.permissions import (
    IsSelfUserOrAdmin,
    IsShopOwnerOrAdmin,
    IsCategoryOwnerOrAdmin,
    IsProductInfoOwnerOrAdmin,
    IsContactOwnerOrAdmin,
)
from app.renderers import UserJSONRenderer
from app.signals import new_order
from app.filters import ProductInfoFilter
from app.models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
    User,
    Order,
    OrderItem,
    Contact,
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
    OrderSerializer,
    OrderUpdateDestroySerializer,
    OrderItemSerializer,
    ContactSerializer,
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
        if request.user.type != "shop":
            return JsonResponse({'Error': "Импорт доступен только для магазинов"}, status=403)

        json_file = request.FILES.get("file")
        if json_file:
            try:
                data = json.load(json_file)
            except Exception:
                return JsonResponse({"Error": "Неверный формат файла"}, status=400)
            
            with transaction.atomic():
                try:
                    shop, _ = Shop.objects.get_or_create(name=data["shop"], user_id=request.user.id)
                except IntegrityError:
                    return JsonResponse({"Error": "У пользователя уже есть магазин"}, status=400)

                categories = data.get("categories")
                if categories is None:
                    return JsonResponse({"Error": "Отсутствуют категории"}, status=400)
                for category in categories:
                    category, _ = Category.objects.get_or_create(name=category["name"])
                    category.shops.add(shop.id)
                    category.save()
            
                items = data.get("items")
                if items is None:
                    return JsonResponse({"Error": "Отсутствуют товары"}, status=400)
                product_infos = []
                product_parameters = []
                for item in items:
                    product, _ = Product.objects.get_or_create(name=item["name"], categories_id=item["category"])
                    product_info = ProductInfo(
                        product=product,
                        shop=shop,
                        price=item["price"],
                        price_rrc=item["price_rrc"],
                        quantity=item["quantity"]
                    )
                    product_infos.append(product_info)

                    # Обработка параметров
                    parameters = item.get("parameters")
                    if parameters is None:
                        return JsonResponse({"Error": "Отсутствуют параметры"}, status=400)
                    
                    for parameter in parameters:
                        for name, value in parameter.items():
                            parameter, _ = Parameter.objects.get_or_create(name=name)
                            product_parameters.append(ProductParameter(
                                product_info=product_info,
                                parameter=parameter,
                                value=value
                            ))

                # Пакетное создание объектов
                ProductInfo.objects.bulk_create(product_infos)
                ProductParameter.objects.bulk_create(product_parameters)

            return JsonResponse({"message": "Успешно"}, status=200)
        else:
            return JsonResponse({"Error": "Файл не загружен"}, status=400)


class RegisterView(CreateAPIView):
    """Класс для регистрации пользователя"""

    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)

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

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return JsonResponse({"message": "Email подтвержден!"}, status=200)

class LoginView(CreateAPIView):
    """Класс для авторизации пользователя"""
    
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def post(self, request: Request):
        # Проверка пароля.
        check_password(request.data["user"]["password"])

        user = request.data.get("user", {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return JsonResponse(serializer.data, status=200)


class UserListView(ListAPIView):
    """Класс для получения списка пользователей"""

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
    permission_classes = (IsAuthenticated, IsSelfUserOrAdmin)


class ShopListView(ListAPIView):
    """Класс для получения списка магазинов"""
    
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)


class ShopDetailView(UpdateAPIView, DestroyAPIView):
    """Класс для обновления и удаления магазина"""
    
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated, IsShopOwnerOrAdmin)


class CategoryListView(ListAPIView):
    """Класс для получения списка категорий"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class CategoryDetailView(UpdateAPIView, DestroyAPIView):
    """Класс для обновления и удаления категорий"""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, IsCategoryOwnerOrAdmin)


class ProductInfoListView(ListAPIView):
    """Класс для получения полного списка товаров со всеми параметрами"""
    
    queryset = ProductInfo.objects.filter(Q(shop__state=True))
    serializer_class = ProductInfoSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductInfoFilter


class ProductInfoView(RetrieveAPIView):
    """Класс для получения полной информации о товаре"""
    
    queryset = ProductInfo.objects.filter(Q(shop__state=True))
    serializer_class = ProductInfoSerializer
    permission_classes = (IsAuthenticated,)


class PartnerProductInfoViewSet(ModelViewSet):
    """Класс для получения, обновления и удаления товаров для партнера"""
    
    def get_queryset(self):
        return ProductInfo.objects.filter(Q(shop__user=self.request.user))

    serializer_class = ProductInfoUpdateDestroySerializer
    permission_classes = (IsAuthenticated, IsProductInfoOwnerOrAdmin)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductInfoFilter


class BasketListView(APIView):
    """Класс для получения, обновления, удаления товаров из корзины"""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        """Метод для получения списка товаров в корзине"""
        
        # Получение корзины пользователя
        basket = Order.objects.filter(
            user_id=request.user.id, state="basket").prefetch_related(
            "order_items__product_info__product__categories",
            "order_items__product_info__product_parameters__parameter").annotate(
            total_sum=Sum(
                F("order_items__quantity") * F("order_items__product_info__price"))
            ).distinct()
        
        serializer = OrderSerializer(basket, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)
    
    def post(self, request: Request):
        """Метод для добавления товара в корзину"""
        
        items_basket = request.data.get("items")
        if items_basket:
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state="basket")
            order_items = []
            # Вызываем конекстный менеджер для атомарности операции
            with transaction.atomic():
                for item in items_basket:
                    item.update({"order": basket.id})
                    serializer = OrderItemSerializer(data=item)
                    if serializer.is_valid():
                        order_items.append(serializer.validated_data)
                    else:
                        return JsonResponse({"Errors": serializer.errors}, status=400)
                OrderItem.objects.bulk_create([OrderItem(**data) for data in order_items])

            return JsonResponse({"Message": "Успешно", "Создано объектов": len(order_items)}, status=200)
        return JsonResponse({"Errors": "Не указаны все необходимые аргументы"}, status=400)
    
    def patch(self, request: Request):
        """Метод для обновления количества товара в корзине"""
        
        items_basket = request.data.get("items")
        if items_basket:
            try:
                basket = Order.objects.get_object_or_404(user_id=request.user.id, state="basket")
            except Http404:
                return JsonResponse({"Errors": "Корзина не найдена"}, status=404)
            update_items = 0
            # Вызываем конекстный менеджер для атомарности операции
            with transaction.atomic():
                for item in items_basket:
                    serializer = OrderItemSerializer(data=item)
                    if serializer.is_valid():
                        try:
                            order_item = OrderItem.objects.get_object_or_404(order_id=basket.id, id=item["id"])
                        except Http404:
                            return JsonResponse({"Errors": "Элемент корзины не найден"}, status=404)
                        else:
                            order_item.quantity = item["quantity"]
                            order_item.save()
                            update_items += 1
                    else:
                        return JsonResponse({"Errors": serializer.errors}, status=400)

            return JsonResponse({"Message": "Успешно", "Обновлено объектов": update_items}, status=200)
        return JsonResponse({"Errors": "Не указаны все необходимые аргументы"}, status=400)
    
    def delete(self, request: Request):
        """Метод для удаления товаров из корзины"""
        
        try:
            basket = Order.objects.get_object_or_404(user_id=request.user.id, state="basket")
        except Http404:
            return JsonResponse({"Errors": "Корзина не найдена"}, status=404)
        else:
            basket.delete()
            return JsonResponse({"Message": "Успешно"}, status=200)


class ContactViewSet(ModelViewSet):
    """Класс для управления контактами"""

    def get_queryset(self):
        # Если пользователь администратор, возвращаем все контакты
        if self.request.user.is_staff:
            return Contact.objects.all()
        # В противном случае возвращаем только контакты текущего пользователя
        return Contact.objects.filter(user=self.request.user)

    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated, IsContactOwnerOrAdmin)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["city", "street"]



class OrderView(ListCreateAPIView):
    """Класс для получения, размещения заказов пользователя"""
    
    def get_queryset(self):
        return Order.objects.filter(
            user_id=self.request.user.id).exclude(state="basket").prefetch_related(
            "order_items__product_info__product__categories",
            "order_items__product_info__product_parameters__parameter"
            ).select_related("contact").annotate(
            total_sum=Sum(
                F("order_items__quantity") *
                F("order_items__product_info__price")
            )).distinct()
    
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request):
        """Метод для размещения заказа"""
        
        basket_id = request.data.get("basket_id")
        contact_id = request.data.get("contact_id")
        if basket_id is None or contact_id is None:
            return JsonResponse({"Errors": "Не указаны все необходимые аргументы"}, status=400)
        
        if not isinstance(basket_id, int) or not isinstance(contact_id, int):
            return JsonResponse({"Errors": "ID корзины и контакта должны быть числами"}, status=400)

        if not Contact.objects.filter(id=contact_id, user_id=self.request.user.id).exists():
            return JsonResponse({"Errors": "Контакт не найден"}, status=400)
        
        try:
            basket = Order.objects.get_object_or_404(user_id=self.request.user.id, state="basket", id=basket_id)
        except Http404:
            return JsonResponse({"Errors": "Корзина не найдена"}, status=404)
        else:
            basket.update(state="new", contact_id=contact_id)
            new_order.send(sender=Order, user_id=self.request.user.id)
            return JsonResponse({"Message": "Заказ успешно размещен"}, status=200)


class PartnerOrderView(ListAPIView, UpdateAPIView):
    """Класс для получения и обновления заказов партнером"""

    permission_classes = (IsAuthenticated,)
    serializer_class = OrderUpdateDestroySerializer
    
    def get_queryset(self):
        return Order.objects.filter(
            order_items__product_info__shop__user_id=self.request.user.id
            ).exclude(state='basket').annotate(
            total_sum=Sum(
                F("order_items__quantity") *
                F("order_items__product_info__price")
            )).distinct()
