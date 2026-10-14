# Internet Shop API

Backend интернет-магазина на **FastAPI + SQLAlchemy + SQLite** с регистрацией и входом через **JWT**.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py                     # тестовые данные (по желанию)
uvicorn main:app --reload
```

Документация: **http://127.0.0.1:8000/docs**

## Файлы

| Файл | Что внутри |
|---|---|
| `database.py` | подключение к SQLite, `get_db()` |
| `auth.py` | хеширование паролей, создание и проверка JWT token |
| `models.py` | таблицы: User, Category, Product, CartItem, Order, OrderItem, Review, Favorite |
| `schemas.py` | что API принимает и отдаёт + валидация |
| `crud.py` | вся логика работы с базой |
| `main.py` | все endpoints и проверки |
| `seed.py` | тестовые данные |

## Связи (relationships)

```
Category ──< Product
User ──< CartItem >── Product
User ──< Order ──< OrderItem >── Product
User ──< Review >── Product
User ──< Favorite >── Product
```

## Авторизация (JWT)

| Метод | Путь | Что делает |
|---|---|---|
| POST | `/register` | регистрация `{name, username, email, phone, password}` |
| POST | `/login` | вход `{username, password}` → `access_token` |
| GET | `/me` | текущий пользователь (нужен token) |

1. `POST /register` — пароль сохраняется только как хеш (`password_hash`, bcrypt).
2. `POST /login` — проверяет username и пароль, возвращает JWT token (живёт 30 минут).
3. В Swagger кнопка **Authorize** → в поле `Authorization` вставить `Bearer <token>`.
4. `GET /me` — `get_current_user` проверяет token и возвращает пользователя.

Пользователи из `seed.py`: `rustam`, `malika`, `daler`, пароль у всех `12345`.

| Ошибка | Причина |
|---|---|
| `Authorization header missing` | header не передан |
| `Invalid authorization format` | token без слова `Bearer` |
| `Invalid token` | token истёк, повреждён или создан с другим `SECRET_KEY` |
| `Invalid username or password` | неверный username или пароль |

## Endpoints

### Пользователи
| Метод | Путь | Что делает |
|---|---|---|
| POST | `/users/` | создать пользователя |
| GET | `/users/` | список пользователей |
| GET | `/users/{user_id}` | один пользователь |
| PUT | `/users/{user_id}` | обновить |
| DELETE | `/users/{user_id}` | удалить (нельзя, если есть заказы) |
| GET | `/users/{user_id}/cart/` | текущая корзина |
| GET | `/users/{user_id}/orders/` | все заказы пользователя |
| GET | `/users/{user_id}/purchases/` | история покупок (без отменённых) |
| GET | `/users/{user_id}/orders/last/` | последний заказ |
| GET | `/users/{user_id}/orders/most-expensive/` | самый дорогой заказ |
| GET | `/users/{user_id}/total-spent/` | сумма всех покупок |
| GET | `/users/{user_id}/orders-count/` | количество заказов |
| GET | `/users/{user_id}/products/` | какие товары покупал |
| GET | `/users/{user_id}/products/{product_id}/count/` | сколько раз покупал товар |
| GET | `/users/{user_id}/statistics/` | статистика пользователя |

### Категории
| Метод | Путь | Что делает |
|---|---|---|
| POST | `/categories/` | создать |
| GET | `/categories/?search=pho&order=desc` | список, поиск и сортировка по названию |
| GET | `/categories/{category_id}` | одна категория |
| PUT | `/categories/{category_id}` | обновить |
| DELETE | `/categories/{category_id}` | удалить (нельзя, если есть товары) |
| GET | `/categories/{category_id}/products/` | товары категории |

### Товары
| Метод | Путь | Что делает |
|---|---|---|
| POST | `/products/` | создать (категория обязательна) |
| GET | `/products/` | список с фильтрами (см. ниже) |
| GET | `/products/{product_id}` | один товар |
| PUT | `/products/{product_id}` | обновить |
| DELETE | `/products/{product_id}` | удалить (нельзя, если есть в активном заказе) |
| GET | `/products/{product_id}/similar/` | похожие товары из той же категории |
| GET | `/products/price/cheap/?limit=5` | самые дешёвые |
| GET | `/products/price/expensive/?limit=5` | самые дорогие |
| GET | `/products/stock/out/` | закончились (stock = 0) |
| GET | `/products/stock/low/` | stock меньше 5 |
| GET | `/products/rating/high/` | средний rating ≥ 4 |
| GET | `/products/rating/low/` | средний rating < 3 |

Фильтры `GET /products/`:

```http
GET /products/?search=phone&category_id=1&min_price=100&max_price=1000&in_stock=true&sort_by=price&order=desc&page=1&page_size=10
```

- `search` — поиск по названию
- `category_id`, `min_price`, `max_price`, `in_stock` — фильтры
- `sort_by` — `id`, `name`, `price`, `stock`; `order` — `asc` / `desc`
- `page`, `page_size` — pagination

### Корзина
| Метод | Путь | Что делает |
|---|---|---|
| POST | `/cart/add/` | добавить товар `{user_id, product_id, quantity}`; если уже есть — quantity увеличивается |
| GET | `/cart/{user_id}` | корзина: товары, subtotal каждого, общая сумма |
| PUT | `/cart/items/{cart_item_id}` | изменить quantity `{quantity}` |
| DELETE | `/cart/items/{cart_item_id}` | удалить товар из корзины |
| DELETE | `/cart/clear/{user_id}` | очистить корзину |

### Заказы
| Метод | Путь | Что делает |
|---|---|---|
| POST | `/orders/create/` | создать заказ из корзины `{user_id}` |
| GET | `/orders/` | все заказы |
| GET | `/orders/{order_id}` | заказ с товарами |
| PUT | `/orders/{order_id}/status/` | изменить статус `{status: new / paid / cancelled}` |
| POST | `/orders/{order_id}/cancel/` | отменить заказ (stock возвращается) |

```http
GET /orders/?status=paid&user_id=1&sort_by=total_price&order=desc&page=1&page_size=10
```

- `status` — `new`, `paid`, `cancelled` (только новые / оплаченные / отменённые)
- `sort_by` — `created_at`, `total_price`, `id`

При создании заказа:
1. корзина не должна быть пустой
2. каждого товара должно хватать на складе
3. цена товара сохраняется в заказе (`OrderItem.price`)
4. stock уменьшается
5. корзина очищается

### Отзывы
| Метод | Путь | Что делает |
|---|---|---|
| POST | `/products/{product_id}/reviews/` | добавить отзыв `{user_id, rating 1–5, text}` |
| GET | `/products/{product_id}/reviews/` | отзывы товара |
| GET | `/products/{product_id}/rating/` | средний rating |
| DELETE | `/reviews/{review_id}` | удалить отзыв |

### Избранное
| Метод | Путь | Что делает |
|---|---|---|
| POST | `/favorites/` | добавить `{user_id, product_id}` (два раза нельзя) |
| GET | `/favorites/{user_id}` | избранное пользователя |
| GET | `/favorites/{user_id}/{product_id}` | есть ли товар в избранном |
| DELETE | `/favorites/{user_id}/{product_id}` | удалить из избранного |

### Статистика
`GET /statistics/` — количество пользователей, товаров, категорий, заказов, общая и средняя сумма заказов, самый продаваемый, самый дорогой и самый дешёвый товар, товары с низким stock, пользователь, который потратил больше всех.

## Проверки

| Правило | Ответ |
|---|---|
| товар без категории / с несуществующей категорией | 404 |
| несуществующий товар или пользователь в корзине | 404 |
| stock = 0 или больше, чем есть на складе | 400 |
| заказ из пустой корзины | 400 |
| quantity < 1, price ≤ 0, stock < 0, rating не 1–5 | 422 |
| удалить товар из активного заказа (`new` / `paid`) | 400 |
| один товар в избранное два раза | 400 |
