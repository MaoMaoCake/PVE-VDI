# What is Proxmox VDI?
Proxmox VDI is a project aimed at leveraging proxmox as a Virtual Desktop environment. This project is based  on proxmox, virt-viewer and noVNC.

# Why use Proxmox VDI? 
Proxmox VDI is a fully open-source system aimed at SMEs to reduce the cost of maintaining desktops infrastructure. PVE-VDI leverages cloudinit and cloud images to support a wide variety of OSes. 

# Features
PVE-VDI comes with multiple features that allow as much flexibility as possible.
- LDAP/SSO Integration
- RBAC
- Self Provisioned Machines 
- Pinned machines
- Temporary machines with generated passwords
- System sharing among users
- User Specified Backup 


# FAQs
## How Does PVE-VDI handle Authentication?
Authentication is done with proxmox's built in authentication system. This built in system has support for LDAP and SSO already built in. For any additional auth method support will need to be added to proxmox directly.

## What are Pinned Machines?
Pinned machines are machines given to a user by the system admin. This is their "main" system that cannot be deleted by the user. 

## What are Self Provisioned Machines? 
Self provisioned machines are machines that the user creates and own.

## What are Temporary Machines? 
Temporary machines are machines that only persist for the duration of the user's login. Once the user is logged out, the machines will be deleted automatically.

## How does Machine Sharing work?
PVE-VDI adds support for machine sharing between users. This support is done using a lock on the provisioning server so 2 users will not be able to connect to the same system at the same time.The system will lock the machine when a user connects preventing other people from connecting. The current user will have to manually release the lock for the other user to be able to log in. This is to make sure that a user cannot be hijacked from the machine they are currently using.

## Can Users backup their systems?
Users are able to back up their machine by themselves and also do a restore on their own.

## Protocols
The aim is to support SPICE and noVNC, but SPICE will be the main priority.

## What OS does PVE-VDI Support? 
PVE-VDI uses cloudinit for it's vm provisioning, therefore it supports a wide variety of OSes. This limitation is only for VMs that are created by the user. The Admins are able to install an OS such as windows on proxmox itself and assign it to a user.