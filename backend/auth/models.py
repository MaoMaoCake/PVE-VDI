from pydantic import BaseModel

from typing import Optional
from fastapi.param_functions import Form


class User(BaseModel):
    username: str
    CSRFToken: str = None
    Ticket: str = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class PVEOAuth2PasswordRequestForm():
    def __init__(
            self,
            username: str = Form(),
            password: str = Form(),
            totp: Optional[str] = Form(default=None),
            realm: Optional[str] = Form(default=None)
    ):
        self.username = username
        self.password = password
        self.totp = totp
        self.realm = realm
