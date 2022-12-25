from pydantic import BaseModel


class PVENode(BaseModel):
    name: str
    node_id: str
    total_memory: str
    total_cpus: float
    status: str


class PVEVM(BaseModel):
    name: str
    total_cpus: int
    total_memory: str
    status: str
    vm_id: int
    type: str = 'qemu'

class PVELXC(BaseModel):
    name: str
    total_cpus: int
    total_memory: str
    status: str
    vm_id: int
    type: str = 'lxc'

class PVENodeList(BaseModel):
    node_list: list[PVENode]


class PVEVMList(BaseModel):
    vm_list: list[PVEVM]

class PVELXCList(BaseModel):
    lxc_list: list[PVELXC]
class PVEGuestList(BaseModel):
    guest_list: list[PVEVM | PVELXC]