from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User


SECRET_KEY = 'CHANGE_THIS_SECRET_KEY'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto'
)


auth_header = APIKeyHeader(
    name='Authorization',
    auto_error=False
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    authorization: str = Depends(auth_header),
    db: Session = Depends(get_db)
):
    if authorization is None:
        raise HTTPException(status_code=401, detail='Authorization header missing')

    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Invalid authorization format. Use: Bearer <token>')

    token = authorization.replace('Bearer ', '', 1).strip()

    if not token:
        raise HTTPException(status_code=401, detail='Token is empty')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('user_id')

        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid token')

    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail='User not found')

    if not user.is_active:
        raise HTTPException(status_code=403, detail='User is not active')

    return user
