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
