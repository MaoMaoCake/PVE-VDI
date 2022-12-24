from fastapi import APIRouter, Depends

from ..auth.utils import get_current_user
from ..auth.models import User
from .utils import get_pve_nodes
from .models import PVENodeList

pveRouter = APIRouter()


@pveRouter.get("/api/pve/nodes", response_model=PVENodeList, tags=["PVE"])
def nodes(current_user: User = Depends(get_current_user)) -> PVENodeList:
    """
    Returns all the nodes that are part of the cluster
    :return:
    """
    return get_pve_nodes(current_user.CSRFToken, current_user.Ticket)

