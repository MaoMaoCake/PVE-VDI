from dotenv import load_dotenv
load_dotenv('backend/backend.env')

from fastapi import FastAPI, Depends
from .auth.route import authRouter
from .pve.routes import pveRouter

app = FastAPI()
app.include_router(authRouter)
app.include_router(pveRouter)