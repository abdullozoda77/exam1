from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

def check_text(value):
    value = value.strip()
    if len(value) < 2:
        raise ValueError('Must be at least 2 characters')
    return value

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str = ''

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        return check_text(value)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()
        if '@' not in value or '.' not in value:
            raise ValueError('Email is not correct')
        return value

class UserRead(UserCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class CategoryCreate(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        return check_text(value)

class CategoryRead(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ProductCreate(BaseModel):
    name: str
    description: str = ''
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category_id: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        return check_text(value)

class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: CategoryRead

class ProductShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: float
    stock: int

class CartAdd(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(default=1, ge=1)

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)

class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product: ProductShort
    quantity: int
    subtotal: float

class CartRead(BaseModel):
    user_id: int
    items: list[CartItemRead]
    total_quantity: int
    total_price: float

class OrderCreate(BaseModel):
    user_id: int

class OrderStatusUpdate(BaseModel):
    status: Literal['new', 'paid', 'cancelled']

class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int | None
    product_name: str
    price: float
    quantity: int
    subtotal: float

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    total_price: float
    created_at: datetime
    items: list[OrderItemRead]

class ReviewCreate(BaseModel):
    user_id: int
    rating: int = Field(ge=1, le=5)
    text: str = ''

class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    product_id: int
    rating: int
    text: str
    created_at: datetime

class FavoriteCreate(BaseModel):
    user_id: int
    product_id: int

class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    product: ProductShort
