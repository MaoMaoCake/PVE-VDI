import os

from datetime import timedelta
from fastapi import Depends, HTTPException, status, APIRouter

from .models import Token, User, PVEOAuth2PasswordRequestForm
from .utils import create_access_token, authenticate_user, get_current_user, get_pve_realm

authRouter = APIRouter()


@authRouter.post("/token", response_model=Token)
async def login_for_access_token(form_data: PVEOAuth2PasswordRequestForm = Depends()) -> dict:
    """
    Takes in form data from the frontend and authenticates the user using the proxmox authentication api.

    :param form_data:
    :return:
    """
    user = authenticate_user(form_data.username, form_data.password, form_data.totp, form_data.realm)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"username": user.username, "ticket": user.Ticket, "CSRFToken": user.CSRFToken},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@authRouter.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """
    This is the endpoint for getting current user.

    :param current_user:
    :return:
    """
    return current_user


@authRouter.get("/api/auth/realms")
def pve_realm():
    return get_pve_realm()
