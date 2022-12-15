# import security modules
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# user model
from .models  import User, TokenData

# creating jwt
from datetime import timedelta, datetime
from jose import JWTError, jwt

# fast API tools
from fastapi import Depends, HTTPException, status

# import env variable tools
import os

# pull the database connector
from ..database.utils import dbexecute


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)

def create_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def get_password_hash(password) -> str:
    return pwd_context.hash(password)

def authenticate_user(username: str , password: str) -> User | None:
    response = dbexecute(f"SELECT id, username, password FROM users WHERE username='{username}'")
    db_user_id, db_username, db_password = response[0]
    if len(response) != 1:
        # this should only ever have 1 since username is unique
        return None
    else:
         if verify_password(plain_password=password, hashed_password=db_password):
             # todo Get roles dynamically
             return User(user_id=db_user_id, username=db_username, role='Admin')
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("OAUTH_SECRET_KEY"), algorithm=os.getenv("OAUTH_ALGORITHM"))
    return encoded_jwt

def get_user(username) -> User | None:
    """
    Gets username and returns the User Class
    :param username:
    :return: User class
    """
    data = dbexecute(f"SELECT id, username FROM users WHERE username='{username}'")
    # the data here should always be 1 since username is unique
    db_user_id, db_username = data[0]
    # todo Get roles dynamically
    return User(user_id=db_user_id, username=db_username, role="Admin")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("OAUTH_SECRET_KEY"), algorithms=[os.getenv("OAUTH_ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user