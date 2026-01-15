from datetime import datetime, timedelta
from typing import Optional, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.schemas.auth import TokenData, User, UserInDB

# OAuth2 scheme – clients will hit /token to get JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store (demo)
users_db: Dict[str, Dict] = {
    "prabal": {
        "username": "prabal",
        "full_name": "prabal gupta",
        "hashed_password": pwd_context.hash("prabal123"),
        "disabled": False,
    },
    "guest": {
        "username": "guest",
        "full_name": "Guest User",
        "hashed_password": pwd_context.hash("guest123"),
        "disabled": False,
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(db: Dict[str, Dict], username: str) -> Optional[UserInDB]:
    if username in db:
        return UserInDB(**db[username])
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(users_db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_error
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_error

    user = get_user(users_db, username=token_data.username)  
    if user is None:
        raise credentials_error
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
