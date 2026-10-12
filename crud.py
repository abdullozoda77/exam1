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
