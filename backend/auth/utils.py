import os
from .models import User
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Optional
import requests
from .errors import NoRealmProvidedException, CredentialsException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str, totp: Optional[str], realm: Optional[str]) -> User | None:
    """
    Takes in
    :param username: str
    :param password: str
    :param totp: Optional[str]
    :param realm: Optional[str]
    :return: User
    """
    # this will be gotten from ENV variable later
    pm_url = 'https://172.16.1.2:8006' + "/api2/json/access/ticket"
    querystring = ""
    if totp:
        # do totp handling here
        pass
    else:
        if realm:
            querystring = {"username": username, "password": password, "realm": realm}
        elif "@" in username:
            querystring = {"username": username, "password": password}
        else:
            raise NoRealmProvidedException

    res = requests.post(pm_url, params=querystring, verify=False)
    if res.status_code == status.HTTP_200_OK:
        data = res.json().get('data')
        username, ticket, CSRF = data.get("username"), data.get("ticket"), data.get("CSRFPreventionToken")
        return User(username=username, Ticket=ticket, CSRFToken=CSRF)
    else:
        return None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str = payload.get("username")
        ticket: str = payload.get("ticket")
        CSRF: str = payload.get("CSRFToken")
        if username is None:
            raise CredentialsException
        return User(username=username, Ticket=ticket, CSRFToken=CSRF)
    except JWTError:
        raise CredentialsException
