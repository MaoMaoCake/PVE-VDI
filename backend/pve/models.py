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


class PVENodeList(BaseModel):
    node_list: list[PVENode]


class PVEVMList(BaseModel):
    vm_list: list[PVEVM]
