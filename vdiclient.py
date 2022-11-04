# import ui
import configparser
import os
import sys
import time

import yaml
import random
import requests
import proxmoxer
import subprocess
from time import sleep
from io import StringIO

import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
class VDIClient:
    # default configs
    tk_root = tk.Tk()
    mainFrame = None
    hosts = [] # the host that we can select
    unique_hosts = set()
    spice_proxy = {} # if we need proxying
    config = None # the config object for the app
    proxmox = None
    scaling = 1
    logged_in = False
    width = 400
    height = 200
    spice_client = None

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

    def get_scaling(self):
        return 1
    def config_ui(self):
        # todo handle scaling
        self.width = 400 * self.get_scaling()
        self.height = 200 * self.get_scaling()

        # if self.config.get("ui").get("fullscreen"):
        #     self.tk_root.attributes('-zoomed', True)

        if self.config.get("ui").get("kiosk"):
            self.tk_root.attributes("-fullscreen", True)

        self.tk_root.title(self.config.get("ui").get('title'))
        self.tk_root.resizable(False, False)
        self.tk_root.geometry(f'{self.width}x{self.height}')
        self.tk_root.grid_rowconfigure(0, weight=1)
        self.tk_root.grid_columnconfigure(0, weight=1)
        self.mainFrame = tk.Frame(self.tk_root, width=self.width, height=self.height)
        self.mainFrame.grid(sticky="nsew")
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=1)
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
    def cancel_login(self):
        self.tk_root.destroy()
    def login_window(self):
        selected_host = tk.StringVar()
        selected_host.set(self.hosts[0].get("name")) # get the first value
        use_totp = self.config.get("proxmox").get("authentication").get("auth_totp")
        self.clear(self.mainFrame)

        width = 20
        tk.Label(self.mainFrame, text="username", width= width ).grid(row=0, column=0, sticky='w')
        username = tk.Entry(self.mainFrame, width=width*2 )
        username.grid(row=0, column=1)

        tk.Label(self.mainFrame, text="password", width=width).grid(row=1, column=0)
        password = tk.Entry(self.mainFrame, show="●", width=width*2)
        password.grid(row=1, column=1)
        if use_totp:
            tk.Label(self.mainFrame, text="TOTP", width=width).grid(row=2, column=0)
            totp = tk.Entry(self.mainFrame, width=width*2)
            totp.grid(row=2, column=1)
        tk.Label(self.mainFrame, text="Host Name", width=width).grid(row=3, column=0)
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
        tk.Button(self.mainFrame, text="Cancel", command=self.cancel_login).grid(row=4,column=0)
    def create_vm_entry(self, vm, parent):
        frame_width = 25
        frame_height = 100
        vmFrame = tk.Frame(parent, width=self.width)
        img = self.get_machine_logo(vm.get("type"))
        panel = tk.Label(vmFrame, image=img, height=frame_height)
        panel.image = img
        panel.grid(row=0, column=0, rowspan=3)
        tk.Label(vmFrame, text=f"{vm.get('name')}", width=frame_width, justify='left').grid(row=0, column=1, columnspan=2)
        tk.Label(vmFrame, text=f"VM:{vm.get('vmid')}", width=frame_width, justify='left').grid(row=1, column=1, columnspan=2)
        tk.Label(vmFrame, text=f"{vm.get('status')}", width=frame_width, justify='left').grid(row=2, column=1, columnspan=2)
        tk.Button(vmFrame, text="Connect", command=lambda: self.run_vm(vm.get('node'), vm.get('vmid'), vm.get('type')))\
        .grid(row=0, rowspan=2, column=4)
        ttk.Separator(vmFrame, orient='horizontal').grid(row=4, column=0 ,columnspan=6, sticky='ew')
        return vmFrame

    def run_vm(self, host_node, vmid, vmtype):
        print(f'trying to run vm{vmid}')
        status = False
        if vmtype == 'qemu':
            vm_status = self.proxmox.nodes(host_node).qemu(str(vmid)).status.get('current')
        elif vmtype == 'lxc':
            vm_status = self.proxmox.nodes(host_node).lxc(str(vmid)).status.get('current')
        else:
            raise NotImplementedError
        if vm_status['status'] != 'running':
            # start VM
            print(f'Starting {vm_status["name"]}...')
            try:
                if vmtype == 'qemu':
                    jobid = self.proxmox.nodes(host_node).qemu(str(vmid)).status.start.post(timeout=28)
                elif vmtype == 'lxc':
                    jobid = self.proxmox.nodes(host_node).lxc(str(vmid)).status.start.post(timeout=28)
                else:
                    raise NotImplementedError
            except proxmoxer.core.ResourceException as e:
                print(f"Unable to start VM, please provide your system administrator with the following error:\n {e!r}")
                return False
            retries = 0
            running = False
            while not running and retries < int(self.config.get('proxmox').get("vm-start-timeout")):
                try:
                    print(f'try {retries}')
                    jobstatus = self.proxmox.nodes(host_node).tasks(jobid).status.get()
                except Exception as e:
                    jobstatus = {}
                    print(e)
                if 'exitstatus' in jobstatus:
                    if jobstatus['exitstatus'] != 'OK':
                        print('Unable to start VM, please contact your system administrator for assistance')
                        break
                    else:
                        running = True
                        status = True
                time.sleep(1)
                retries += 1
            if not status:
                return status
        if vmtype == 'qemu':
            vm_spice_config = self.proxmox.nodes(host_node).qemu(str(vmid)).spiceproxy.post()
        elif vmtype == 'lxc':
            vm_spice_config = self.proxmox.nodes(host_node).lxc(str(vmid)).spiceproxy.post()
        else:
            raise NotImplementedError
        spiceconfigParser = configparser.ConfigParser()
        spiceconfigParser['virt-viewer'] = {}
        spice_proxy = self.config.get('proxmox').get('SpiceProxyRedirect')
        for key, value in vm_spice_config.items():
            if key == 'proxy':
                val = value[7:].lower()
                if val == spice_proxy.get('from'):
                    spiceconfigParser['virt-viewer'][key] = f'http://{spice_proxy.get("to")}'
                else:
                    spiceconfigParser['virt-viewer'][key] = f'{value}'
            else:
                spiceconfigParser['virt-viewer'][key] = f'{value}'
        # todo support extra virt viwer config
        if self.config.get("virt-viewer"):
            # for key, value
            pass
        inifile = StringIO('')
        spiceconfigParser.write(inifile)
        inifile.seek(0)
        inistring = inifile.read()
        if self.config.get('debug').get('config-viewer'):
            # todo: show config
            pass
        vv_cmd = [str(self.spice_client).strip()]
        if self.config.get("ui").get('kiosk'):
            vv_cmd.append('--kiosk')
            vv_cmd.append('--kiosk-quit')
            vv_cmd.append('on-disconnect')
        elif self.config.get("ui").get('fullscreen'):
            vv_cmd.append('--full-screen')
        vv_cmd.append('-') # listen to stdin
        process = subprocess.Popen(vv_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            output = process.communicate(input=inistring.encode('utf-8'), timeout=5)[0]
        except subprocess.TimeoutExpired:
            pass
        status = True
        return status
        # # run virt viewer with the config
        # subprocess.Popen()
    def vm_window(self):
        vm_list = self.get_vms()
        print(vm_list)
        if vm_list:
            self.clear(self.mainFrame)
            # get vm list
            canvas = tk.Canvas(self.mainFrame)
            scrollbar = tk.Scrollbar(self.mainFrame, orient=tk.VERTICAL, command=canvas.yview)
            scrollFrame = tk.Frame(canvas, width=self.width)
            scrollFrame.grid_rowconfigure(0, weight=1)
            scrollFrame.grid_columnconfigure(0, weight=1)
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.create_window((0, 0), window=scrollFrame, anchor="nw", width=self.width)
            for vm in vm_list:
                self.create_vm_entry(vm, scrollFrame).grid(sticky="nsew")
            canvas.grid(row=0, column=0)
            scrollbar.grid(row=0, rowspan=10, column=1, sticky=tk.N + tk.S)

            # bind the scroll with the canvas
            scrollFrame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
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
        # check that virtviewer exists and is runnable
        self.check_virt_viewer()
        self.login_window()
        self.tk_root.mainloop()

    def get_machine_logo(self,type):
        img = Image.open(f"assets/{type}.png")
        if type == 'qemu':
            img = img.resize((60,50), Image.ANTIALIAS)
        if type == 'lxc':
            img = img.resize((60, 60), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        return img

    def check_virt_viewer(self):
        try:
            if os.name == 'nt':  # Windows
                import csv
                cmd1 = 'ftype VirtViewer.vvfile'
                result = subprocess.check_output(cmd1, shell=True)
                cmdresult = result.decode('utf-8')
                cmdparts = cmdresult.split('=')
                for row in csv.reader([cmdparts[1]], delimiter=' ', quotechar='"'):
                    self.spice_client = row[0]
                    break

            elif os.name == 'posix':
                cmd1 = 'which remote-viewer'
                result = subprocess.check_output(cmd1, shell=True)
                self.spice_client = 'remote-viewer'
        except subprocess.CalledProcessError:
            if os.name == 'nt':
                print('Installation of virt-viewer missing, please install from https://virt-manager.org/download/')
            elif os.name == 'posix':
                print('Installation of virt-viewer missing, please install using `apt install virt-viewer`')
            sys.exit()


if __name__ == "__main__":
    app = VDIClient(config_path="config.yaml")
    app.run()