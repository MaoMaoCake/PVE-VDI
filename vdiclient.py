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
    proxmox = None
    scaling = 1
    logged_in = False

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
    def pve_auth(self, username, selected_host, passwd=None, totp=None):
        print(self.hosts)
        err = None
        connected = False
        authenticated = False
        proxmox_conf = self.config.get("proxmox")
        for hostinfo in self.hosts:
            # set the selected host
            if hostinfo["name"] == selected_host:
                host = hostinfo['ip']
                port = hostinfo['port']
                try:
                    # try token login if token exist
                    token = proxmox_conf.get("token")
                    backend = proxmox_conf.get("authentication").get("auth_backend")
                    verify = proxmox_conf.get("authentication").get("tls_verify")
                    if token:
                        self.proxmox = proxmoxer.ProxmoxAPI(host, user=f'{username}@{backend}', token_name=token.get("name"),
                                                         token_value=token.get("value"), verify_ssl=verify, port=port)
                    # if the user is using totp
                    elif totp:
                        self.proxmox = proxmoxer.ProxmoxAPI(host, user=f'{username}@{backend}', otp=totp, password=passwd,
                                                         verify_ssl=verify, port=port)
                    # else login with username password
                    else:
                        self.proxmox = proxmoxer.ProxmoxAPI(host, user=f'{username}@{backend}', password=passwd,
                                                         verify_ssl=verify, port=port)
                    connected = True
                    authenticated = True
                    return connected, authenticated, err
                # if can connect but cannot auth
                except proxmoxer.backends.https.AuthenticationError as e:
                    err = e
                    connected = True
                    return connected, authenticated, err
                # unable to connect to url
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout,
                        requests.exceptions.ConnectionError) as e:
                    err = e
                    connected = False
        return connected, authenticated, err


if __name__ == "__main__":
    app = VDIClient(config_path="config.yaml")
    app.run()