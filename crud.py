from sqlalchemy import func
from sqlalchemy.orm import Session
from models import User, Category, Product, CartItem, Order, OrderItem, Review, Favorite

def get_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, pk: int):
    return db.query(User).filter(User.id == pk).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, data):
    user = User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, pk: int, data):
    user = get_user(db, pk)
    if not user:
        return None
    user.name = data.name
    user.email = data.email
    user.phone = data.phone
    db.commit()
    db.refresh(user)
    return user

def get_categories(db: Session, search: str | None = None, order: str = 'asc'):
    query = db.query(Category)
    if search is not None:
        query = query.filter(Category.name.contains(search))
    if order == 'desc':
        query = query.order_by(Category.name.desc())
    else:
        query = query.order_by(Category.name.asc())
    return query.all()

def get_category(db: Session, pk: int):
    return db.query(Category).filter(Category.id == pk).first()

def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()

def create_category(db: Session, data):
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def update_category(db: Session, pk: int, data):
    category = get_category(db, pk)
    if not category:
        return None
    category.name = data.name
    db.commit()
    db.refresh(category)
    return category

def get_category_products(db: Session, category_id: int):
    return db.query(Product).filter(Product.category_id == category_id).all()

def delete_category(db: Session, pk: int):
    category = get_category(db, pk)
    if not category:
        return None
    db.delete(category)
    db.commit()
    return category

def get_product(db: Session, pk: int):
    return db.query(Product).filter(Product.id == pk).first()

def create_product(db: Session, data):
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, pk: int, data):
    product = get_product(db, pk)
    if not product:
        return None
    product.name = data.name
    product.description = data.description
    product.price = data.price
    product.stock = data.stock
    product.category_id = data.category_id
    db.commit()
    db.refresh(product)
    return product

def get_products(
    db: Session,
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    sort_by: str = 'id',
    order: str = 'asc',
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Product)

    if search is not None:
        query = query.filter(Product.name.contains(search))

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if in_stock is True:
        query = query.filter(Product.stock > 0)

    if in_stock is False:
        query = query.filter(Product.stock == 0)

    sort_columns = {
        'id': Product.id,
        'name': Product.name,
        'price': Product.price,
        'stock': Product.stock
    }

    column = sort_columns.get(sort_by, Product.id)

    if order == 'desc':
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())

    return query.offset(skip).limit(limit).all()

def get_similar_products(db: Session, product):
    return db.query(Product).filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).all()

def get_cheap_products(db: Session, limit: int = 5):
    return db.query(Product).order_by(Product.price.asc()).limit(limit).all()

def get_expensive_products(db: Session, limit: int = 5):
    return db.query(Product).order_by(Product.price.desc()).limit(limit).all()

def get_out_of_stock_products(db: Session):
    return db.query(Product).filter(Product.stock == 0).all()

def get_low_stock_products(db: Session, max_stock: int = 5):
    return db.query(Product).filter(Product.stock < max_stock).order_by(Product.stock.asc()).all()

def get_cart_item(db: Session, user_id: int, product_id: int):
    return db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id
    ).first()

def add_to_cart(db: Session, data):
    item = get_cart_item(db, data.user_id, data.product_id)
    if item:
        item.quantity += data.quantity
    else:
        item = CartItem(**data.model_dump())
        db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_cart_items(db: Session, user_id: int):
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()

def get_cart(db: Session, user_id: int):
    items = get_cart_items(db, user_id)
    return {
        'user_id': user_id,
        'items': items,
        'total_quantity': sum(item.quantity for item in items),
        'total_price': round(sum(item.subtotal for item in items), 2)
    }

def get_cart_item_by_id(db: Session, pk: int):
    return db.query(CartItem).filter(CartItem.id == pk).first()

def update_cart_item(db: Session, pk: int, quantity: int):
    item = get_cart_item_by_id(db, pk)
    if not item:
        return None
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item

def delete_cart_item(db: Session, pk: int):
    item = get_cart_item_by_id(db, pk)
    if not item:
        return None
    item.product
    db.delete(item)
    db.commit()
    return item

def clear_cart(db: Session, user_id: int):
    count = db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    return count

def create_order(db: Session, user_id: int):
    items = get_cart_items(db, user_id)
    order = Order(user_id=user_id, status='new', total_price=0)
    total = 0

    for item in items:
        order.items.append(OrderItem(
            product_id=item.product_id,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity
        ))
        item.product.stock -= item.quantity
        total += item.product.price * item.quantity
        db.delete(item)

    order.total_price = round(total, 2)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_orders(
    db: Session,
    status: str | None = None,
    user_id: int | None = None,
    sort_by: str = 'created_at',
    order: str = 'desc',
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Order)

    if status is not None:
        query = query.filter(Order.status == status)

    if user_id is not None:
        query = query.filter(Order.user_id == user_id)

    sort_columns = {
        'id': Order.id,
        'created_at': Order.created_at,
        'total_price': Order.total_price
    }

    column = sort_columns.get(sort_by, Order.created_at)

    if order == 'desc':
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())

    return query.offset(skip).limit(limit).all()

def get_order(db: Session, pk: int):
    return db.query(Order).filter(Order.id == pk).first()

def cancel_order(db: Session, order):
    for item in order.items:
        product = get_product(db, item.product_id) if item.product_id else None
        if product:
            product.stock += item.quantity
    order.status = 'cancelled'
    db.commit()
    db.refresh(order)
    return order

def update_order_status(db: Session, order, status: str):
    if status == 'cancelled':
        return cancel_order(db, order)
    order.status = status
    db.commit()
    db.refresh(order)
    return order
