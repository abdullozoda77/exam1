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
