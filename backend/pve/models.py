from pydantic import BaseModel


class PVENode(BaseModel):
    name: str
    node_id: str
    total_memory: str
    total_cpus: float
    status: str

class PVEVM(BaseModel):
    name: str


class PVENodeList(BaseModel):
    node_list: list[PVENode]