from fastapi import APIRouter, Depends

from ..auth.utils import get_current_user
from ..auth.models import User
from .utils import get_pve_nodes, get_vm_from, get_lxc_from
from .models import PVENodeList, PVEVMList, PVEGuestList

pveRouter = APIRouter()


@pveRouter.get("/api/pve/nodes", response_model=PVENodeList, tags=["PVE"])
def nodes(current_user: User = Depends(get_current_user)) -> PVENodeList:
    """
    Returns all the nodes that are part of the cluster
    :return:
    """
    return get_pve_nodes(current_user.CSRFToken, current_user.Ticket)


@pveRouter.get("/api/pve/{node}/vms", response_model=PVEGuestList, tags=["PVE"])
def get_vm(node: str, type: str = "all", current_user: User = Depends(get_current_user)) -> PVEGuestList:
    vms = get_vm_from(node, current_user.CSRFToken, current_user.Ticket)
    lxc = get_lxc_from(node, current_user.CSRFToken, current_user.Ticket)
    if type == "qemu":
        return PVEGuestList(guest_list= vms.vm_list)
    elif type == 'lxc':
        return PVEGuestList(guest_list= lxc.lxc_list)
    else:
        all_list = []
        all_list.extend(vms.vm_list)
        all_list.extend(lxc.lxc_list)
        return PVEGuestList(guest_list= all_list)