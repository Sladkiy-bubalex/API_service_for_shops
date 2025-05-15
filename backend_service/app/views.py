import json
from rest_framework.request import Request
from django.http import JsonResponse
from rest_framework.views import APIView
from app.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


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
                
            return JsonResponse({"Status": "Успешно"}, status=200)
        else:
            return JsonResponse({"Error": "Файл не загружен"}, status=400)



