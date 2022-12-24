from dotenv import load_dotenv
load_dotenv('backend/backend.env')

from fastapi import FastAPI
from .auth.route import authRouter
from .pve.routes import pveRouter

description = """
PVE VDI is a VDI solution for proxmox
"""

tags_metadata = [
    {
        "name": "Auth",
        "description": "Authentication Endpoint for interfacing with PVE",
    },
    {
        "name": "PVE",
        "description": "Proxmox Proxy Endpoints",
    },
]

app = FastAPI(
    title="PVE-VDI",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata
)
app.include_router(authRouter)
app.include_router(pveRouter)