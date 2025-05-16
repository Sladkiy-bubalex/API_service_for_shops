import json
from django.contrib.auth.password_validation import validate_password
from rest_framework.request import Request
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from app.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, User
from app.serializers import RegisterUserSerializer
from rest_framework.exceptions import ValidationError


class ImportItemView(APIView):
    
    def post(self, request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Error': "Требуется авторизация"}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Error': "Импорт доступен только для магазинов"}, status=403)

        json_file = request.data.FILES.get("file")
        if json_file:
            try:
                data = json.load(json_file)
            except Exception:
                return JsonResponse({"Error": "Неверный формат файла"}, status=400)
            
            shop, _ = Shop.objects.get_or_create(name=data["shop"], user=request.user.id)
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
    serializer_class = RegisterUserSerializer

    def post(self, request):
        # Проверка пароля.
        try:
            validate_password(request.data["password"])
        except ValidationError as e:
            return JsonResponse({"Error": f"Ошибка проверка пароля: {e}"}, status=400)

        # Проверка входящих данных и последующее сохрание в БД.
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User(
                email=serializer.validated_data["email"],
                first_name=serializer.validated_data.get("first_name"),
                last_name=serializer.validated_data.get("last_name"),
                username=serializer.validated_data["username"],
                type=serializer.validated_data["type"],
                company=request.data.get("company"),
                position=request.data.get("position")
            )
            user.set_password(serializer.validated_data["password"])  # Хэшируем пароль
            user.save()
            return JsonResponse({"message": "Вы успешно зарегистрированы!"}, status=201)

        return JsonResponse({"Errors": serializer.errors}, status=400)
