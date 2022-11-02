# import ui
import os
import sys
import random
import requests
import proxmoxer
import subprocess
from time import sleep
from io import StringIO

class VDIClient:
    # default configs
    hosts = []
    spice_proxy = {}
    proxmox = None
    scaling = 1
    title = "VDI Login"
    backend = 'pve'
    user = ""
    token_name = None
    token_value = None
    totp = False
    kiosk = False
    fullscreen = True
    verify_ssl = True
    icon = None
    additional_params = None
    # theme = 'LightBlue'
    guest_type = 'both'
    config = None
    logged_in = False

    def __init__(self, config):
        # loadconfig
        self.config = config # parse yaml
        pass



if __name__ == "__main__":
    app = VDIClient(config="filename")
    app.run()