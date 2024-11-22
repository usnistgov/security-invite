# Security InVITE ([In]tegrated [VI]rtualized [T]est [E]nvironment)

*Dmitry Cousin*  
*Eric Trapnell*  
*Mark Trapnell*  

NIST

September 6, 2024


## Disclaimer
Any mention of commercial products or reference to commercial organizations is for information only; it does not imply recommendation or endorsement by NIST, nor does it imply that the products mentioned are necessarily the best available for the purpose.

## What is Security Invite?
- Security Invite automates testing of assignments independent of the tools used for development, interface, and data persistence.
- It promotes sharing of security-specific testing and education while enhancing student's skills in cyber-security-conscious programming

## Topics Covered
- Students shall perform a few examples of user input sanitization, including handling the following:
    - plain user inputs, 
    - inputs that can break file storage, 
    - inputs that can present problems in JSON/YAML storage, 
    - and various SQL-injections 
- Improve password storage with hashing,padding/salting, and crunching/peppering
    - demonstrate a use of rainbow tables against the DBMS with USER IDs
    - demonstrate a more advanced use of the accompanying data in the DBMS for deeper than simple rainbow table attacks.
    - explain/demonstrate computational complexity of the attacks
    - include references to NIST resources regarding passwords


## Initial Setup - Configuring the Host System

### 0) For Windows Hosts Only, Install Git for Windows and Python3
If you're using a Windows operating system, Install Git for Windows from https://git-scm.com/download/win. Complete the installation using the default settings, or customize to your liking. Git for Windows (aka Git Bash) will allow you to easily run commands in this guide that direct you to perform a task "in a Terminal."

After the installation is complete, start the program Git Bash. Run the command `python3` to launch the Windows store. Install python3 from the Windows store.

### 1) Download Oracle VirtualBox (This guide was written using 7.1.2)
Security InVITE is designed to test code implementations deployed into a virtual machine. To accomplish this, we will download and install VirtualBox.

* Download VirtualBox from https://www.virtualbox.org/wiki/Downloads
* Install VirtualBox using the default installer instructions. If prompted, download any missing dependencies.

### 2) Python 3.11 or later must be installed on the host machine
Run this command in a Terminal window to check the python3 version:  
`python3 --version`

If the python3 version is lower than 3.11 please see https://www.python.org/downloads/ for newer versions. 

### 3) Download Security InVITE project files

Ensure that the desired branch is checked out and current on the Host machine at ~/git/security-invite  

To download the project code, run the following in a Terminal window: 
* `mkdir ~/git`  
* `cd ~/git`   
* `git clone git@github.com:usnistgov/security-invite.git`  

## Creating a VirtualBox Virtual Machine (VM) for Security InVITE Testing
These steps provide detailed instructions for the configuration of a virtual machine with Ubuntu Server and sshd. The guide assumes installation of Ubuntu Server 24.04, but can be used for other versions of Ubuntu (and potentially adapted to other Linux distributions).

### Download and Validate the Ubuntu iso
* Download the Ubuntu Server iso at http://releases.ubuntu.com/24.04/.
* In a terminal window, compute its cryptographic hash value as follows:

```
shasum -a 256 /path/to/ubuntu-server.iso
```

* Compare the sha256 of the iso file against the value found by going to http://releases.ubuntu.com/24.04/ and selecting the SHA256SUMS file. Find the SHA sum for the version you downloaded. The values should be identical.

### Create and Configure the Virtual Machine (VM)
After downloading and verifying the Ubuntu iso, it's time to create and configure the VM and finally install Ubuntu inside it. 

#### Create the VM
* Start VirtualBox
* Select "New" from the toolbar to create a new virtual machine
* Enter a Name and the following operating system information
    * Select the downloaded Ubuntu iso from the ISO Image dropdown list (or if you don't see it, select the Other button and navigate to the download location)
    * The Create Virtual Machine dialog window may auto detect the OS and version information. If it doesn't, make the following selections:
        * Type: Linux
        * Version: Ubuntu (64-bit)
    * Check the "Skip Unattended Installation" check box

* Select the following hardware options:
    * Base Memory: 2048MB
    * Processors: 2

* Make the following hard disk selections:
    * Select the "Create a Virtual Hard Disk Now" radio button
    * Set the size of the virtual hard disk to 15.00GB

* Select "Finish"

#### Begin the Ubuntu installation
Now we are ready to install the Ubuntu OS into our VM.

* Select the VM in the VirtualBox Manager window
* Select "Start"
* Select "Try or Install Ubuntu Server"
* Choose English
* If prompted to update the installer, Select "Continue without updating"
* On the keyboard configuration screen, select "Done"
* Choose Ubuntu Server then select "Done"
* On the network connections screen, select "Done"
* On the configure proxy screen, select "Done"
* On the configure Ubuntu archive mirror screen, select "Done"
* On the guided storage configuration screen, select "Done"
* On the storage configuration screen, select "Done"
* If prompted to confirm destructive action, select "Continue"
* "Profile setup" dialog:
    * Your name: sir
    * Your server's name: si_server
    * Pick a username: sir
    * Choose and confirm a password for the sir user
    * Select "Done"
* On the upgrade to Ubuntu Pro screen, ensure "Skip for now" is chosen, then select "Continue"
* On the SSH Setup screen, ensure "Install OpenSSH server" is chosen, then select "Done"
* On the Featured Server Snaps screen, select "Done"
* Once the install is finished, select "Reboot Now"
* If prompted to remove installation media, just press enter to continue.

##  Setup the Homework Environment

### Enable the SSH forwarding port
* In the Virtualbox VM manager, select the VM you created and go to Settings > Network > Advanced
* Select Port Forwarding
* Select the Add new port forwarding rule button
* In the Host Port column, enter an unused port (such as 44321)
* In the Guest Port column, enter 22
* Select OK to complete the port assignment
* Select OK to save the changes

### Create and install SSH private/public key pair
In a Terminal window on the host machine, do the following:
* `ssh-keygen -t ed25519 -f ~/.ssh/si_key`
* Enter a passphrase
* `ssh-copy-id -p 44321 -i ~/.ssh/si_key.pub sir@localhost`
* Type 'yes' and press enter when prompted
* Enter the user's password when prompted
* Test out the key by running `ssh -p 44321 -i ~/.ssh/si_key sir@localhost`
* Enter the key's passphrase
* `exit` the SSH session 

### Install homework assignment(s) in the VM
Make sure to name the homework files hw1.py, hw2.py hw3.py and hw4.py. Run the following command, making sure to replace '/path/to/homework/' with the path on your system:  
`scp -r -P 44321 -i ~/.ssh/si_key /path/to/homework/ sir@localhost:~/`

### Copy setup scripts to the VM
`scp -r -P 44321 -i ~/.ssh/si_key security-invite/topics/Tests/si/ sir@localhost:~/`

### Copy requirements.txt to the VM
First copy the requirements.txt file from the security invite repository, by running the following on the host system:  
`scp -r -P 44321 -i ~/.ssh/si_key security-invite/topics/0-Docker/si-requirements.txt sir@localhost:~/requirements.txt`

On the VM, first install pip:  
`sudo apt install python3-pip`

Still on the VM, run `pip install -r requirements.txt` so that all dependencies for the test_homework.py script will be installed. The command will overwrite installed versions of the dependencies in the text file.

Next, run the following commands on the VM:
```
cd ~/si
python3 db_create.py -wd ./db -pm set_db/map_ubu.yaml -db SI_DB.db
python3 db_create.py -wd ./db -pm set_db/map_ubu+.yaml -db SI-HW4.db
```

### Run the automatic testing
 Replace `/path/to/test_homework.py` with the path to `test_homework.py` and `VM_USERNAME` with the VM's user name and run the following command on the host system:  
`python3 security-invite/topics/Tests/si/test_homework.py -k ~/.ssh/si_key -w 44321 -hw 1 -u VM_USERNAME`  
If you wish to test other assignments, replace the `-hw 1` argument with `-hw #` of the one you are trying test.


## Build Docker Containers
### Installing Docker Engine
Docker Engine is needed to run containers. The installation guide is available at https://docs.docker.com/engine/install. Alternatively, Rancher Desktop is available at https://rancherdesktop.io/.

### Container Setup
First, open a terminal window and clone the security invite git repository:
`git clone git@github.com:usnistgov/security-invite.git`

Copy all homework files to a directory that will be put into the container by the setup script.
`cp hw1 hw2 hw3 hw4 security-invite/topics/Tests`

Run the following commands to build the sid container:  

```
cd security-invite/topics
docker build -t sid ./ -f dockerfile
```

Run the container in detached mode:  
`docker run -d -p 2222:22 --name si_container sid`

Generate an SSH key and copy it to the container. The password set for the user created in the dockerfile will need to be used here:  
```
ssh-keygen -t ed25519 -f ~/.ssh/si_key
ssh-copy-id -p 2222 -i ~/.ssh/si_key.pub sir@localhost
```

Run the test_homework.py script against all homework files in the container by changing the -hw option to the desired homework #:  
`python3 Tests/si/test_homework.py -k ~/.ssh/si_key -w 2222 -hw 1 -u sir`

## Provide requirements.txt if additional packages are required to run the completed homework assignment
If additional python packages are used during development of any of the homework assignments, then `pip freeze > requirements.txt` should be run on the VM or the container. The requirements.txt file needs to be submitted along with the homework assignments so that the test system can have a matching python environment.
