# Make sure that Rancher and Rancher VM-Environment 
# Pull docker container image with ubuntu 22.04
docker pull ubuntu:22.04

# Run the downloaded image
docker run -it -p 8022:22 ubuntu:22.04 

# If you don't mind the waiting time
# apt update && apt upgrade -y

# Install Open-SSH Server in the image
#apt update && apt install -y openssh-server

# Install Python
apt update && apt install -y python3

# Install Pip (to run pip list)
apt update && apt install -y pip

# make sure that YAML package is installed
sudo apt-get install python-yaml
python3 -m pip install pyyaml

# IP Configuration tooling including ifconfig
sudo apt install net-tools


python3 ./si/test_homework.py -a localhost -f ./report -w 50000 -k /Users/dac4/toolchain/ssh_keys/uap_vm_pri -u sid -hw 4

scp -r -P 50000 ./Tests/* toolchain@localhost:~/

# Creating new user

sudo adduser sid 
usermod -aG sudo sid