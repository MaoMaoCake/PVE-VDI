# What is Proxmox VDI?
Proxmox VDI is a project aimed at leveraging proxmox as a Virtual Desktop environment.

# Why use Proxmox VDI? 
Proxmox VDI is a fully open-source system aimed at SMEs to reduce the cost of maintaing desktops infrastructure. PVE-VDI leverages cloudinit and cloud images to support a wide variety of OSes. 

# Features
PVE-VDI comes with multiple features that allow as much flexibility as possible.
- LDAP Integration
- RBAC
- Self Provisioned Machines 
- Pinned machines
- Temporary machines with generated passwords
- System sharing among users
- User Specified Backup 

## What are Pinned Machines?
Pinned machines are machines given to a user by the system admin. This is their "main" system that cannot be deleted by the uesr. 

## What are Self Provisioned Machines? 
Self provisioned machines are machines that the user creates and own.

## What are Temporary Machines? 
Temporary machines are machines that only persist for the duration of the user's login. Once the user is logged out, the machines will be deleted automatically.
