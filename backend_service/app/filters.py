from django_filters import rest_framework as filters
from app.models import ProductInfo


class ProductInfoFilter(filters.FilterSet):
    """Фильтры для объявлений."""
    
    shop = filters.CharFilter(field_name="shop__name")
    product = filters.CharFilter(field_name="product__name")
    price = filters.RangeFilter(field_name="price")

    class Meta:
        model = ProductInfo
        fields = [
            "shop",
            "product",
            "price"
        ]