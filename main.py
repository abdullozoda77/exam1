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
