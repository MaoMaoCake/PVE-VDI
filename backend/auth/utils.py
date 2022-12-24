# for env variables
import os

# making jwt
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

# utility imports
from fastapi import Depends, status
from typing import Optional

# define models
from .models import User, PVERealmList, PVERealm
from .errors import NoRealmProvidedException, CredentialsException

# requests library
import requests
import urllib3
urllib3.disable_warnings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str, totp: Optional[str], realm: Optional[str]) -> User | None:
    """
    Takes in authentication parameters and authenticates them with proxmox.

    :param username: str
    :param password: str
    :param totp: Optional[str]
    :param realm: Optional[str]
    :return: User
    """
    # this will be gotten from ENV variable later
    pm_url = os.getenv("PVE_URL") + "/api2/json/access/ticket"
    querystring = {"username": username, "password": password}
    if totp:
        querystring['totp'] = totp
    if realm:
        querystring["realm"] = realm
    if not realm and "@" not in username:
        raise NoRealmProvidedException

    res = requests.post(pm_url, params=querystring, verify=False)
    if res.status_code == status.HTTP_200_OK:
        data = res.json().get('data')
        username, ticket, CSRF = data.get("username"), data.get("ticket"), data.get("CSRFPreventionToken")
        return User(username=username, Ticket=ticket, CSRFToken=CSRF)
    else:
        return None


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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


def get_pve_realm() -> PVERealmList:
    """
    Gets the authentication realm from proxmox
    :return:
    """
    realm_list = []
    pve_url = os.getenv("PVE_URL") + "/api2/json/access/domains"
    res = requests.get(pve_url).json()
    for realm in res.get('data'):
        realm_list.append(PVERealm(name=realm.realm))
    return PVERealmList(pve_realms=realm_list)