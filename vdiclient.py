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

import tkinter as tk
from tkinter import ttk
class VDIClient:
    # default configs
    tk_root = tk.Tk()
    mainFrame = tk.Frame(tk_root)
    mainFrame.grid()
    hosts = [] # the host that we can select
    unique_hosts = set()
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
        for host in self.hosts:
            self.unique_hosts.add(host.get("name"))
        proxy = self.config.get("proxmox").get("SpiceProxyRedirect")
        if proxy:
            self.spice_proxy = proxy
        self.config_ui()
    def config_ui(self):
        self.tk_root.title(self.config.get("ui").get('title'))
    def pve_auth(self, username, selected_host, passwd=None, totp=None):
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

    # utility for tkinter
    def clear(self, object):
        slaves = object.grid_slaves()
        for x in slaves:
            x.destroy()
    def login(self, *args, **kwargs):
        connected, authenticated, err = self.pve_auth(*args, **kwargs)
        if connected and authenticated:
            print("Connected")
            self.vm_window()
        elif connected and not authenticated:
            print("wrong username or password", err)
        elif not connected:
            print("Connection to the server cannot be established", err)
    def login_window(self):
        selected_host = tk.StringVar()
        selected_host.set(next(iter(self.unique_hosts))) # get the first value
        use_totp = self.config.get("proxmox").get("authentication").get("auth_totp")
        self.clear(self.mainFrame)

        tk.Label(self.mainFrame, text="username").grid(row=0, column=0)
        username = tk.Entry(self.mainFrame)
        username.grid(row=0, column=1)

        tk.Label(self.mainFrame, text="password").grid(row=1, column=0)
        password = tk.Entry(self.mainFrame)
        password.grid(row=1, column=1)
        if use_totp:
            tk.Label(self.mainFrame, text="TOTP").grid(row=2, column=0)
            totp = tk.Entry(self.mainFrame)
            totp.grid(row=2, column=1)
        tk.Label(self.mainFrame, text="Host Name").grid(row=3, column=0)
        tk.OptionMenu(self.mainFrame, selected_host, *self.unique_hosts).grid(row=3, column=1)
        # different submit button
        if use_totp:
            tk.Button(self.mainFrame, text="Login", command=lambda:
                self.login(username=username.get(), selected_host=selected_host.get(),
                              passwd=password.get(), totp=totp.get()))\
                                .grid(row=4, column=1)
        else:
            tk.Button(self.mainFrame, text="Login", command=lambda:
            self.login(username=username.get(), selected_host=selected_host.get(),
                          passwd=password.get())) \
                .grid(row=4, column=1)

    def create_vm_entry(self, vm, parent):
        vmFrame = tk.Frame(parent)
        tk.Label(vmFrame, text=f"{vm.get('type')}").grid(row=0, column=0, rowspan=2)
        tk.Label(vmFrame, text=f"{vm.get('name')}").grid(row=0, column=1, columnspan=2)
        tk.Label(vmFrame, text=f"VM:{vm.get('vmid')}").grid(row=1, column=1, columnspan=2)
        tk.Label(vmFrame, text=f"{vm.get('status')}").grid(row=2, column=1, columnspan=2)
        tk.Button(vmFrame, text="Connect").grid(row=0, rowspan=2, column=4)
        return vmFrame

    def vm_window(self):
        vm_list = self.get_vms()
        print(vm_list)
        if vm_list:
            self.clear(self.mainFrame)
            # get vm list
            canvas = tk.Canvas(self.mainFrame)
            scrollbar = tk.Scrollbar(self.mainFrame, orient=tk.VERTICAL, command=canvas.yview)
            scrollFrame = tk.Frame(canvas)
            scrollFrame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            canvas.create_window((0, 0), window=scrollFrame, anchor="nw")

            canvas.configure(yscrollcommand=scrollbar.set)
            for vm in vm_list:
                self.create_vm_entry(vm, scrollFrame).grid()
            canvas.grid(row=0, column=0)
            scrollbar.grid(row=0, rowspan=10, column=1, sticky=tk.N + tk.S)
        else:
            # show empty
            pass

    def get_vms(self):
        vms = []
        try:
            wanted_vms = self.config.get("proxmox").get("show-vm-type")
            for vm in self.proxmox.cluster.resources.get(type='vm'):
                if 'template' in vm and vm['template']: # skip templates
                    continue
                if wanted_vms == 'all': # get all vms
                    vms.append(vm)
                elif wanted_vms == vm['type']: # get only the ones we want
                    vms.append(vm)
            return vms
        except proxmoxer.core.ResourceException as e:
            print(f"Unable to display list of VMs:\n {e!r}", 'OK')
            return False
    def run(self):
        self.login_window()
        self.tk_root.mainloop()


if __name__ == "__main__":
    app = VDIClient(config_path="config.yaml")
    app.run()