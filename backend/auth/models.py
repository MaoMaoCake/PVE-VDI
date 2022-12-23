from pydantic import BaseModel

class User(BaseModel):
    username: str
    CSRFToken: str = None
    Ticket: str = None

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None