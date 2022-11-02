# import ui
import os
import sys
import yaml
import random
import requests
import proxmoxer
import subprocess
from time import sleep
from io import StringIO

class VDIClient:
    # default configs
    hosts = [] # the host that we can select
    spice_proxy = {} # if we need proxying
    config = None # the config object for the app

    def __init__(self, config_path):
        # loadconfig
        with open(config_path, "r") as f:
            try:
                self.config = yaml.safe_load(f) # parse yaml
            except yaml.YAMLError as e:
                print(e)
        # set the host vars
        self.hosts = self.config.get("host")
        proxy = self.config.get("proxmox").get("SpiceProxyRedirect")
        if proxy:
            self.spice_proxy = proxy

if __name__ == "__main__":
    app = VDIClient(config_path="config.yaml")
    app.run()