from typing import Literal
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from schemas import *
from crud import *

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Internet Shop API')

def user_or_404(db, user_id):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f'User #{user_id} not found')
    return user

@app.post('/users/', response_model=UserRead)
def user_create(data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail='This email is already used')
    return create_user(db, data)

@app.get('/users/', response_model=list[UserRead])
def users_list(db: Session = Depends(get_db)):
    return get_users(db)

@app.get('/users/{user_id}', response_model=UserRead)
def user_detail(user_id: int, db: Session = Depends(get_db)):
    return user_or_404(db, user_id)

@app.put('/users/{user_id}', response_model=UserRead)
def user_update(user_id: int, data: UserCreate, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    other = get_user_by_email(db, data.email)
    if other and other.id != user_id:
        raise HTTPException(status_code=400, detail='This email is already used')
    return update_user(db, user_id, data)

def category_or_404(db, category_id):
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f'Category #{category_id} not found')
    return category

@app.post('/categories/', response_model=CategoryRead)
def category_create(data: CategoryCreate, db: Session = Depends(get_db)):
    if get_category_by_name(db, data.name):
        raise HTTPException(status_code=400, detail='This category already exists')
    return create_category(db, data)

@app.get('/categories/', response_model=list[CategoryRead])
def categories_list(
    search: str | None = Query(None, min_length=1),
    order: Literal['asc', 'desc'] = 'asc',
    db: Session = Depends(get_db)
):
    return get_categories(db, search, order)

@app.get('/categories/{category_id}', response_model=CategoryRead)
def category_detail(category_id: int, db: Session = Depends(get_db)):
    return category_or_404(db, category_id)

@app.put('/categories/{category_id}', response_model=CategoryRead)
def category_update(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    category_or_404(db, category_id)
    other = get_category_by_name(db, data.name)
    if other and other.id != category_id:
        raise HTTPException(status_code=400, detail='This category already exists')
    return update_category(db, category_id, data)

@app.get('/categories/{category_id}/products/', response_model=list[ProductRead])
def category_products(category_id: int, db: Session = Depends(get_db)):
    category_or_404(db, category_id)
    return get_category_products(db, category_id)

@app.delete('/categories/{category_id}', response_model=CategoryRead)
def category_delete(category_id: int, db: Session = Depends(get_db)):
    category_or_404(db, category_id)
    if get_category_products(db, category_id):
        raise HTTPException(status_code=400, detail='This category has products, it can not be deleted')
    return delete_category(db, category_id)

def product_or_404(db, product_id):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f'Product #{product_id} not found')
    return product

@app.post('/products/', response_model=ProductRead)
def product_create(data: ProductCreate, db: Session = Depends(get_db)):
    category_or_404(db, data.category_id)
    return create_product(db, data)

@app.get('/products/{product_id}', response_model=ProductRead)
def product_detail(product_id: int, db: Session = Depends(get_db)):
    return product_or_404(db, product_id)

@app.put('/products/{product_id}', response_model=ProductRead)
def product_update(product_id: int, data: ProductCreate, db: Session = Depends(get_db)):
    product_or_404(db, product_id)
    category_or_404(db, data.category_id)
    return update_product(db, product_id, data)

@app.get('/products/', response_model=list[ProductRead])
def products_list(
    search: str | None = Query(None, min_length=1),
    category_id: int | None = Query(None, ge=1),
    min_price: float | None = Query(None, gt=0),
    max_price: float | None = Query(None, gt=0),
    in_stock: bool | None = None,
    sort_by: Literal['id', 'name', 'price', 'stock'] = 'id',
    order: Literal['asc', 'desc'] = 'asc',
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    return get_products(
        db=db,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=page_size
    )

@app.get('/products/{product_id}/similar/', response_model=list[ProductRead])
def products_similar(product_id: int, db: Session = Depends(get_db)):
    product = product_or_404(db, product_id)
    return get_similar_products(db, product)

@app.get('/products/price/cheap/', response_model=list[ProductRead])
def products_cheap(limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    return get_cheap_products(db, limit)

@app.get('/products/price/expensive/', response_model=list[ProductRead])
def products_expensive(limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)):
    return get_expensive_products(db, limit)

@app.get('/products/stock/out/', response_model=list[ProductRead])
def products_out_of_stock(db: Session = Depends(get_db)):
    return get_out_of_stock_products(db)

@app.get('/products/stock/low/', response_model=list[ProductRead])
def products_low_stock(db: Session = Depends(get_db)):
    return get_low_stock_products(db)

@app.post('/cart/add/', response_model=CartItemRead)
def cart_add(data: CartAdd, db: Session = Depends(get_db)):
    user_or_404(db, data.user_id)
    product = product_or_404(db, data.product_id)

    if product.stock == 0:
        raise HTTPException(status_code=400, detail=f'«{product.name}» is out of stock')

    item = get_cart_item(db, data.user_id, data.product_id)
    in_cart = item.quantity if item else 0
    if in_cart + data.quantity > product.stock:
        raise HTTPException(status_code=400, detail=f'Only {product.stock} of «{product.name}» in stock, you already have {in_cart} in the cart')

    return add_to_cart(db, data)

@app.get('/cart/{user_id}', response_model=CartRead)
def cart_detail(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_cart(db, user_id)

@app.get('/users/{user_id}/cart/', response_model=CartRead)
def user_cart(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_cart(db, user_id)

@app.put('/cart/items/{cart_item_id}', response_model=CartItemRead)
def cart_item_update(cart_item_id: int, data: CartItemUpdate, db: Session = Depends(get_db)):
    item = get_cart_item_by_id(db, cart_item_id)
    if not item:
        raise HTTPException(status_code=404, detail='Cart item not found')
    if data.quantity > item.product.stock:
        raise HTTPException(status_code=400, detail=f'Only {item.product.stock} of «{item.product.name}» in stock')
    return update_cart_item(db, cart_item_id, data.quantity)

@app.delete('/cart/items/{cart_item_id}', response_model=CartItemRead)
def cart_item_delete(cart_item_id: int, db: Session = Depends(get_db)):
    item = delete_cart_item(db, cart_item_id)
    if not item:
        raise HTTPException(status_code=404, detail='Cart item not found')
    return item

@app.delete('/cart/clear/{user_id}')
def cart_clear(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    count = clear_cart(db, user_id)
    return {'user_id': user_id, 'deleted_items': count}

@app.post('/orders/create/', response_model=OrderRead)
def order_create(data: OrderCreate, db: Session = Depends(get_db)):
    user_or_404(db, data.user_id)
    items = get_cart_items(db, data.user_id)

    if not items:
        raise HTTPException(status_code=400, detail='The cart is empty')

    for item in items:
        if item.quantity > item.product.stock:
            raise HTTPException(status_code=400, detail=f'Only {item.product.stock} of «{item.product.name}» in stock')

    return create_order(db, data.user_id)

def order_or_404(db, order_id):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f'Order #{order_id} not found')
    return order

@app.get('/orders/', response_model=list[OrderRead])
def orders_list(
    status: Literal['new', 'paid', 'cancelled'] | None = None,
    user_id: int | None = Query(None, ge=1),
    sort_by: Literal['id', 'created_at', 'total_price'] = 'created_at',
    order: Literal['asc', 'desc'] = 'desc',
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    return get_orders(db, status, user_id, sort_by, order, skip, page_size)

@app.get('/orders/{order_id}', response_model=OrderRead)
def order_detail(order_id: int, db: Session = Depends(get_db)):
    return order_or_404(db, order_id)

@app.put('/orders/{order_id}/status/', response_model=OrderRead)
def order_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = order_or_404(db, order_id)
    if order.status == 'cancelled':
        raise HTTPException(status_code=400, detail='This order is cancelled, its status can not be changed')
    return update_order_status(db, order, data.status)

@app.post('/orders/{order_id}/cancel/', response_model=OrderRead)
def order_cancel(order_id: int, db: Session = Depends(get_db)):
    order = order_or_404(db, order_id)
    if order.status == 'cancelled':
        raise HTTPException(status_code=400, detail='This order is already cancelled')
    return cancel_order(db, order)

@app.delete('/products/{product_id}', response_model=ProductRead)
def product_delete(product_id: int, db: Session = Depends(get_db)):
    product_or_404(db, product_id)
    if product_in_active_order(db, product_id):
        raise HTTPException(status_code=400, detail='This product is in an active order, it can not be deleted')
    return delete_product(db, product_id)

@app.delete('/users/{user_id}', response_model=UserRead)
def user_delete(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    if user_has_orders(db, user_id):
        raise HTTPException(status_code=400, detail='This user has orders, it can not be deleted')
    return delete_user(db, user_id)

@app.get('/users/{user_id}/orders/', response_model=list[OrderRead])
def user_orders(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_orders(db, user_id=user_id, limit=1000)

@app.get('/users/{user_id}/purchases/', response_model=list[OrderRead])
def user_purchases(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_user_purchases(db, user_id)

@app.get('/users/{user_id}/orders/last/', response_model=OrderRead)
def user_last_order(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    order = get_last_order(db, user_id)
    if not order:
        raise HTTPException(status_code=404, detail='This user has no orders')
    return order

@app.get('/users/{user_id}/orders/most-expensive/', response_model=OrderRead)
def user_most_expensive_order(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    order = get_most_expensive_order(db, user_id)
    if not order:
        raise HTTPException(status_code=404, detail='This user has no orders')
    return order

@app.get('/users/{user_id}/total-spent/')
def user_total_spent(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return {'user_id': user_id, 'total_spent': get_user_total_spent(db, user_id)}

@app.get('/users/{user_id}/orders-count/')
def user_orders_count(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return {'user_id': user_id, 'orders_count': len(get_user_purchases(db, user_id))}

@app.get('/users/{user_id}/products/')
def user_products(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_user_purchased_products(db, user_id)

@app.get('/users/{user_id}/products/{product_id}/count/')
def user_product_count(user_id: int, product_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_user_product_count(db, user_id, product_id)

@app.get('/users/{user_id}/statistics/')
def user_statistics(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_user_statistics(db, user_id)

@app.post('/products/{product_id}/reviews/', response_model=ReviewRead)
def review_create(product_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    product_or_404(db, product_id)
    user_or_404(db, data.user_id)
    return create_review(db, product_id, data)

@app.get('/products/{product_id}/reviews/', response_model=list[ReviewRead])
def product_reviews(product_id: int, db: Session = Depends(get_db)):
    product_or_404(db, product_id)
    return get_product_reviews(db, product_id)

@app.get('/products/{product_id}/rating/')
def product_rating(product_id: int, db: Session = Depends(get_db)):
    product_or_404(db, product_id)
    return get_product_rating(db, product_id)

@app.delete('/reviews/{review_id}', response_model=ReviewRead)
def review_delete(review_id: int, db: Session = Depends(get_db)):
    review = delete_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail='Review not found')
    return review

@app.get('/products/rating/high/')
def products_high_rating(db: Session = Depends(get_db)):
    return get_products_by_rating(db, high=True)

@app.get('/products/rating/low/')
def products_low_rating(db: Session = Depends(get_db)):
    return get_products_by_rating(db, high=False)

@app.post('/favorites/', response_model=FavoriteRead)
def favorite_add(data: FavoriteCreate, db: Session = Depends(get_db)):
    user_or_404(db, data.user_id)
    product_or_404(db, data.product_id)
    if get_favorite(db, data.user_id, data.product_id):
        raise HTTPException(status_code=400, detail='This product is already in favorites')
    return add_favorite(db, data)

@app.get('/favorites/{user_id}', response_model=list[FavoriteRead])
def user_favorites(user_id: int, db: Session = Depends(get_db)):
    user_or_404(db, user_id)
    return get_user_favorites(db, user_id)

@app.get('/favorites/{user_id}/{product_id}')
def favorite_check(user_id: int, product_id: int, db: Session = Depends(get_db)):
    return {
        'user_id': user_id,
        'product_id': product_id,
        'is_favorite': get_favorite(db, user_id, product_id) is not None
    }

@app.delete('/favorites/{user_id}/{product_id}', response_model=FavoriteRead)
def favorite_delete(user_id: int, product_id: int, db: Session = Depends(get_db)):
    favorite = get_favorite(db, user_id, product_id)
    if not favorite:
        raise HTTPException(status_code=404, detail='This product is not in favorites')
    return delete_favorite(db, favorite)

@app.get('/statistics/')
def statistics(db: Session = Depends(get_db)):
    return get_statistics(db)
