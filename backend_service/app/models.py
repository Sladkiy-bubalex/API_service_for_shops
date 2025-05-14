from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator


STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)

class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(
        verbose_name='Компания',
        max_length=40,
        blank=True
    )
    position = models.CharField(
        verbose_name='Должность',
        max_length=40,
        blank=True
    )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=50,
        help_text=_(
            '''Обязательно. 50 символов или меньше.
               Только буквы, цифры и @/./+/-/_'''
        ),
        validators=[username_validator],
        error_messages={
            'unique': _("Пользователь с таким именем уже существует."),
        },
    )
    is_active = models.BooleanField(
        _('активен'),
        default=False,
        help_text=_(
            'Определяет, следует ли считать этого пользователя активным. '
            'Снимите этот флажок вместо удаления учетной записи.'
        ),
    )
    type = models.CharField(
        verbose_name='Тип пользователя',
        choices=USER_TYPE_CHOICES,
        max_length=5, default='buyer'
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)


class Shop(models.Model):
    name = models.CharField(verbose_name='Название', max_length=50)
    url = models.URLField(verbose_name='Ссылка', blank=True, null=True)
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    state = models.BooleanField(
        verbose_name='Статус приема заказов',
        default=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('name',)


class Category(models.Model):
    name = models.CharField(verbose_name='Название', max_length=40)
    shops = models.ManyToManyField(
        Shop,
        verbose_name='Магазины',
        related_name='categories',
        blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('name',)


class Product(models.Model):
    name = models.CharField(verbose_name='Название', max_length=40)
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='products',
        blank=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('name',)


class ProductInfo(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='product_infos',
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name='Магазин',
        related_name='product_infos',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=10, decimal_places=2
    )
    price_rrc = models.DecimalField(
        verbose_name='Рекомендуемая розничная цена',
        max_digits=10,
        decimal_places=2
    )
    quantity = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.product} {self.shop}'

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Список информации о продуктах"
        ordering = ('product',)
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'shop'],
                name='unique_product_shop'
            )
        ]


class Parameter(models.Model):
    name = models.CharField(verbose_name='Название', max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        ordering = ('name',)


class ProductParameter(models.Model):
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='product_parameters',
        on_delete=models.CASCADE
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name='Параметр',
        related_name='product_parameters',
        on_delete=models.CASCADE
    )
    value = models.CharField(verbose_name='Значение', max_length=40)

    def __str__(self):
        return f'{self.product_info} {self.parameter}'

    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = "Список параметров продуктов"
        ordering = ('product_info',)
        constraints = [
            models.UniqueConstraint(
                fields=['product_info', 'parameter'],
                name='unique_product_info_parameter'
            )
        ]


class Contact(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='contacts',
        on_delete=models.CASCADE
    )
    city = models.CharField(verbose_name='Город', max_length=40)
    street = models.CharField(verbose_name='Улица', max_length=40)
    house = models.CharField(verbose_name='Дом', max_length=10)
    building = models.CharField(verbose_name='Корпус', max_length=10, blank=True)
    apartment = models.CharField(verbose_name='Квартира', max_length=10, blank=True)
    phone = models.CharField(verbose_name='Телефон', max_length=20)

    def __str__(self):
        return f'{self.user} {self.city} {self.street} {self.house} {self.apartment} {self.phone}'

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"
        ordering = ('user',)


class Order(models.Model):
    user = models.ForeignKey(
        User, verbose_name='Пользователь',
        related_name='orders',
        blank=True,
        on_delete=models.CASCADE
    )
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(
        verbose_name='Статус',
        choices=STATE_CHOICES,
        max_length=15,
        default='basket'
    )
    contact = models.ForeignKey(
        Contact,
        verbose_name='Контакт',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user} {self.dt} {self.state} {self.contact}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('user',)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='order_items',
        on_delete=models.CASCADE
    )
    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='order_items',
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.order} {self.product_info} {self.quantity}'

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = "Список позиций заказов"
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product_info'],
                name='unique_order_product_info'
            )
        ]


class ConfirmEmailToken(models.Model):
    
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь, связанный с этим токеном подтверждения Email")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Когда был создан этот токен")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Ключ"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Подтверждение Email для пользователя {user}".format(user=self.user)