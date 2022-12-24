import os

import requests

from .models import PVENode, PVENodeList
import math

def convert_size(size_bytes: int) -> str:
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def get_pve_nodes(csrf: str, token: str) -> PVENodeList | None:
    node_list = []
    pve_url = os.getenv("PVE_URL") + "/api2/json/nodes"
    headers = {"CSRFPreventionToken": csrf,
               "Cookie": "PVEAuthCookie=" + token}
    res = requests.get(pve_url, headers=headers, verify=False)
    if res.status_code == 200:
        data = res.json().get("data")
        for entry in data:
            node = entry.get("node")
            node_id = entry.get("id")
            total_memory = entry.get("maxmem")
            total_cpus = entry.get("maxcpu")
            status = entry.get("status")
            node_list.append(PVENode(name=node,
                                     node_id=node_id,
                                     total_memory=convert_size(total_memory),
                                     total_cpus = total_cpus,
                                     status=status))
        return PVENodeList(node_list=node_list)
    else:
        return None
