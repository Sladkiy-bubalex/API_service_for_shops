# Точки входа

## Для регистрации пользователя
POST /api/v1/register/

### Формат запроса

```json
{
    "email": "string", (обязательное)
    "username": "string", (обязательное)
    "password": "string", (обязательное)
    "first_name": "string", (необязательное)
    "last_name": "string", (необязательное)
    "type": "string", (необязательное)
    "company": "string", (необязательное)
    "position": "string" (необязательное)
}
```
- email - email пользователя
- username - никнейм пользователя
- password - пароль пользователя
- first_name - имя пользователя
- last_name - фамилия пользователя
- type - тип пользователя (buyer, shop)
- company - компания пользователя
- position - должность пользователя

### Формат ответа

```json
{
    "id": "integer",
    "email": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "type": "string",
    "company": "string",
    "position": "string"
}
```

## Для подтверждения Email
POST /api/v1/confirm-email/

### Формат запроса

```json
{
    "key": "string", (обязательное)
    "user": "integer" (обязательное)
}
```

- key - ключ подтверждения из письма
- user - id пользователя

## Для авторизации пользователя
POST /api/v1/login/

### Формат запроса

```json
{
    "user": {
        "email": "string", (обязательное)
        "password": "string" (обязательное)
    }
}
```

### Формат ответа

```json
{
    "email": "string",
    "token": "string"
}
```

## Для получения данных о пользователе (только для авторизованных пользователей)
GET /api/v1/users/

### Описание
Получение данных о пользователе по информации из токена

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "email": "string",
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "company": "string",
        "position": "string",
        "is_active": "boolean",
        "type": "string"
    }
]
```
## Для обновления, удаления, получения данных о пользователе (только для администраторов)
- GET /api/v1/users/
- PATCH /api/v1/users/\<int:id>
- PUT /api/v1/users/\<int:id>
- DELETE /api/v1/users/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "email": "string", (опциональное)
    "username": "string", (опциональное)
    "first_name": "string", (опциональное)
    "last_name": "string", (опциональное)
    "type": "string", (опциональное)
    "company": "string", (опциональное)
    "position": "string" (опциональное)
}
```

## Для получения данных о магазинах или магазине (только для авторизованных пользователей)
- GET /api/v1/shops/
- GET /api/v1/shops/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "name": "string",
        "user": "integer",
        "url": "string",
        "state": "boolean"
    }
]
```

## Для обновления, удаления данных магазина (только для владельца магазина или администраторов)

- PATCH /api/v1/shops/\<int:id>
- PUT /api/v1/shops/\<int:id>
- DELETE /api/v1/shops/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "name": "string", (опциональное)
    "user": "integer", (опциональное)
    "url": "string", (опциональное)
    "state": "boolean" (опциональное)
}
```

## Для получения данных о категориях или категории (только для авторизованных пользователей)
- GET /api/v1/categories/
- GET /api/v1/categories/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "name": "string",
        "shops": "integer"
    }
]
```

## Для обновления, удаления данных категории (только для владельца категории или администраторов)

- PATCH /api/v1/categories/\<int:id>
- PUT /api/v1/categories/\<int:id>
- DELETE /api/v1/categories/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "name": "string", (опциональное)
    "shops": "integer" (опциональное)
}
```

## Для получения данных о товарах или товаре (только для авторизованных пользователей)
- GET /api/v1/products/
- GET /api/v1/products/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "product": {
            "id": "integer",
            "name": "string",
            "categories": "integer"
        },
        "shop": {
            "id": "integer",
            "name": "string",
            "url": "string",
            "user": "integer",
            "state": "boolean"
        },
        "price": "Decimal",
        "price_rrc": "Decimal",
        "quantity": "integer",
        "product_parameters": []
    }
]
```

## Для обновления, удаления данных товара (только для владельца товара или администраторов)

- PATCH /api/v1/products/partner/\<int:id>
- PUT /api/v1/products/partner/\<int:id>
- DELETE /api/v1/products/partner/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
        "id": "integer",
        "product": {
            "id": "integer",
            "name": "string" (изменяемое),
            "categories": "integer" (изменяемое)
        },
        "shop": {
            "id": "integer",
            "name": "string" (изменяемое),
            "url": "string" (изменяемое),
            "user": "integer",
            "state": "boolean" (изменяемое)
        },
        "price": "Decimal" (изменяемое),
        "price_rrc": "Decimal" (изменяемое),
        "quantity": "integer" (изменяемое),
        "product_parameters": [
            {
                "id": "integer",
                "product_info": "integer",
                "parameter": "integer",
                "value": "string" (изменяемое)
            }
        ]
    }
```

## Для получения данных о корзине (только для авторизованных пользователей)
- GET, POST, DELETE, PATCH /api/v1/basket/

### Формат запроса для получения корзины

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "user": "integer",
        "state": "string",
        "dt": "string",
        "contact": {
            "id": "integer",
            "user": "integer",
            "city": "string",
            "street": "string",
            "house": "integer",
            "building": "integer",
            "apartment": "integer",
            "phone": "string"
        },
        "order_items": [
            {
                "id": "integer",
                "product_info": "integer",
                "quantity": "integer"
            },
            {
                "id": "integer",
                "product_info": "integer",
                "quantity": "integer"
            }
        ],
        "total_sum": "Decimal"
    }
]
```

### Формат запроса для добавления товара в корзину

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "items": [
        {
            "product_info": "integer",
            "quantity": "integer"
        }
    ]
}
```

### Формат ответа

```json
{
    "Message": "Успешно",
    "Создано объектов": "integer"
}
```

### Формат запроса для обновления количества товара в корзине

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "items": [
        {
            "id": "integer",
            "quantity": "integer"
        }
    ]
}
```
- id - id элемента корзины
- quantity - количество товара

### Формат ответа

```json
{
    "Message": "Успешно",
    "Обновлено объектов": "integer"
}
```

### Формат запроса для удаления товара из корзины

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "items": [
        {
            "id": "integer"
        }
    ]
}
```

### Формат ответа

```json
{
    "Message": "Успешно",
    "Удалено объектов": "integer"
}
```

## Для управления контактами пользователя(только для авторизованных пользователей)
- GET /api/v1/contacts/
- POST, DELETE, PATCH /api/v1/contacts/\<int:id>

### Формат запроса на получение контактов

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "user": "integer",
        "city": "string",
        "street": "string",
        "house": "integer",
        "building": "integer",
        "apartment": "integer",
        "phone": "string"
    }
]
```

### Формат запроса на добавление, обновление, удаление контакта

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "city": "string", (опциональное)
    "street": "string", (опциональное)
    "house": "integer", (опциональное)
    "building": "integer", (опциональное)
    "apartment": "integer", (опциональное)
    "phone": "string" (опциональное)
}
```

## Для получения данных о заказах (только для авторизованных пользователей)
- GET /api/v1/orders/

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "user": "integer",
        "state": "string",
        "dt": "string",
        "contact": {
            "id": "integer",
            "user": "integer",
            "city": "string",
            "street": "string",
            "house": "integer",
            "building": "integer",
            "apartment": "integer",
            "phone": "string"
        },
        "order_items": [
            {
                "id": "integer",
                "product_info": "integer",
                "quantity": "integer"
            },
            {
                "id": "integer",
                "product_info": "integer",
                "quantity": "integer"
            }
        ],
        "total_sum": "Decimal"
    }
]
```

## Для размещения заказа (только для авторизованных пользователей)
- POST /api/v1/orders/

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

body:{
    "basket_id": "integer",
    "contact_id": "integer"
}
```

### Формат ответа

```json
{
    "Message": "Заказ успешно размещен"
}
```

## Для получения данных о заказах (только для партнеров)
- GET /api/v1/orders/partner/

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}
```

### Формат ответа

```json
[
    {
        "id": "integer",
        "user": "integer",
        "state": "string",
        "dt": "string",
        "contact": {
            "id": "integer",
            "user": "integer",
            "city": "string",
            "street": "string",
            "house": "integer",
            "building": "integer",
            "apartment": "integer",
            "phone": "string"
        },
        "order_items": [
            {
                "id": "integer",
                "product_info": "integer",
                "quantity": "integer"
            },
            {
                "id": "integer",
                "product_info": "integer",
                "quantity": "integer"
            }
        ],
        "total_sum": "Decimal"
    }
]
```

## Для обновления данных заказа (только для партнеров)

- PATCH /api/v1/orders/\<int:id>
- PUT /api/v1/orders/\<int:id>

### Формат запроса

```json
header:{
    "Authorization": "Token <token>" (обязательное)
}

```json
[
    {
        "id": "integer",
        "user": "integer",
        "state": "string" (изменяемое),
        "dt": "string",
        "contact": {
            "id": "integer",
            "user": "integer",
            "city": "string",
            "street": "string",
            "house": "integer",
            "building": "integer",
            "apartment": "integer",
            "phone": "string"
        },
        "order_items": [
            {
                "id": "integer",
                "product_info": "integer",
                "quantity": "integer" (изменяемое)
            }
        ],
        "total_sum": "Decimal"
    }
]
