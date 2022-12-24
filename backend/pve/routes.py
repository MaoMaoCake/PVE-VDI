from fastapi import APIRouter

pveRouter = APIRouter()


@pveRouter.get("/api/pve/nodes", tags=["PVE"])
def nodes():
    return None
