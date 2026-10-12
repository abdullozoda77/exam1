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
