#!/usr/bin/python3

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties.  Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain.  NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

'''
This module is responsible for creating, importing, starting, stopping,
and deleting virtual machines. The module is used by the vmimport and
hellovm modules. This module uses the VBoxManage command-line interface
commands and various modules from the python standard library to
implement the virtual machine test_old subsystem of the Toolchain
Intrastructure (TCI). The script aims to follow the coding conventions
described in the PEP8 (www.python.org/dev/peps/pep-0008) style guide
for python code. Details regarding the virtualbox SDK can be found in
the Oracle VM VirtualBox Programming Guide and Reference found at:
http://download.virtualbox.org/virtualbox/SDKRef.pdf
'''

import subprocess
import sys
import time
import os
import si_server_utils as utils

__author__ = "Chris Bean, Chris Johnson, Lee Badger"
__status__ = "Prototype"


def host_ssh(user, command, time_sec):
    """Run the passed command as the macos user on the host."""
    return server_ssh(user, '192.168.0.5', command, time_sec)


def server_ssh(user, ip_address, command, time_sec=30):
    """Run the passed command as the current user on the mac host at
    ip_address.
    Returns the string from the command's execution on the server.
    Assumes the server is up.
    Assumes that the file hw.pri key is in the /toolchain/ssh_keys dir.
    """
    try:
        result = subprocess.run(['ssh',
                                 user + '@' + ip_address,
                                 '-i', utils.VMS_HW_KEY_PATH,
                                 '-o', 'IdentitiesOnly=yes',
                                 '-o', 'StrictHostKeyChecking=no',
                                 '-q',
                                 command],
                                timeout=time_sec,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return 'CalledProcessError'
    except subprocess.TimeoutExpired:
        return 'TimeoutError'
    return result


def get_vm_home_si():
    

# def retrieve_macos_user():
#     '''
#     Retrieve the macos user name
#     '''
#     try:
#         with open('/home/tciadmin/macos_user', encoding='utf8') as user_file:
#             return user_file.read().strip()
#     except IOError:
#         print('/home/tciadmin/macos_user file does not exist')
#         sys.exit(1)


def is_virtualized():
    '''
    Determine if code is being run in a virtual machine
    '''
    return bool(os.path.isdir(utils.VMS_VIRTUAL_OVA_DIR)
                and os.path.isdir(utils.VMS_VIRTUAL_VBOX_DIR))


def list_running_vms(user, virtualized):
    '''
    List running virtual machines
    '''
    timeout_in_secs = 30

    if virtualized:
        vm_names = host_ssh(user, '/usr/local/bin/vboxmanage list runningvms',
                            timeout_in_secs)
        if vm_names == 'CalledProcessError':
            return 'FAIL - Unable to list running virtual machines'
        if vm_names == 'TimeoutError':
            return 'FAIL - The list running virtual machines operation \
            took longer than %f seconds' % timeout_in_secs
    else:
        try:
            vm_names = subprocess.run(['VBoxManage', 'list', 'runningvms'],
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      timeout=timeout_in_secs)
        except subprocess.CalledProcessError:
            return 'FAIL - Unable to list running virtual machines'
        except subprocess.TimeoutExpired:
            return 'FAIL - The list running virtual machines operation \
            took longer than %f seconds' % timeout_in_secs
    vm_names = vm_names.stdout.decode('utf-8')
    vm_names = vm_names.strip()
    return vm_names


def list_vms(user, virtualized):
    '''
    List registered virtual machines
    '''
    timeout_in_secs = 30

    if virtualized:
        vm_names = host_ssh(user, '/usr/local/bin/vboxmanage list vms',
                            timeout_in_secs)
        if vm_names == 'CalledProcessError':
            return 'FAIL - Unable to list registered virtual machines'
        if vm_names == 'TimeoutError':
            return 'FAIL - The list virtual machines operation took longer\
                    than %f seconds' % timeout_in_secs
    else:
        try:
            vm_names = subprocess.run(['VBoxManage', 'list', 'vms'],
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      timeout=timeout_in_secs)
        except subprocess.CalledProcessError:
            return 'FAIL - FAIL - Unable to list registered virtual machines.'
        except subprocess.TimeoutExpired:
            return 'FAIL - The list virtual machines operation took longer\
                    than %f seconds' % timeout_in_secs
    vm_names = vm_names.stdout.decode('utf-8')
    vm_names = vm_names.strip()
    return vm_names


def dry_run_import(user, ova_file, virtualized):
    '''
    Perform a dry-run import of the virtual appliance (.ova)
    '''
    timeout_in_secs = 300

    if virtualized:
        import_command = '/usr/local/bin/vboxmanage import -n ' + ova_file
        import_result = host_ssh(user, import_command, timeout_in_secs)
        if import_result == 'CalledProcessError':
            return 'FAIL - Dry-run import could not be completed.'
        if import_result == 'TimeoutError':
            return 'FAIL - Dry run import took longer than %f \
            seconds' % timeout_in_secs
    else:
        try:
            import_result = subprocess.run(['VBoxManage', 'import',
                                            '-n', ova_file],
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           timeout=timeout_in_secs)
        except subprocess.CalledProcessError:
            return 'FAIL - Dry-run import could not be completed.'
        except subprocess.TimeoutExpired:
            return 'FAIL - Dry run import took longer than %f \
            seconds' % timeout_in_secs
    import_result = import_result.stdout.decode('utf-8')
    import_result = import_result.strip()
    return import_result


def full_import(user, ova_file, virtualized):
    '''
    Perform a full import of the virtual appliance file (.ova)
    '''
    timeout_in_secs = 300
    if virtualized:
        import_command = '/usr/local/bin/vboxmanage import ' + ova_file
        full_results = host_ssh(user, import_command, timeout_in_secs)
        if full_results == 'CalledProcessError':
            return 'FAIL - Full import of vm could not be completed.'
        if full_results == 'TimeoutError':
            return 'FAIL - Import took longer than %f \
            seconds' % timeout_in_secs
    else:
        try:
            full_results = subprocess.run(['VBoxManage', 'import', ova_file],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          timeout=timeout_in_secs)
        except subprocess.CalledProcessError:
            return 'FAIL - Full import of vm could not be completed.'
        except subprocess.TimeoutExpired:
            return 'FAIL - Import took longer than %f \
            seconds' % timeout_in_secs
    full_results = full_results.stdout.decode('utf-8')
    full_results = full_results.strip()
    return full_results


def delete_forwarding_port(user, vm_name, port_name, virtualized):
    '''
    Delete forwarding port in virtual machine
    '''
    timeout_in_secs = 5

    if virtualized:
        command = ('/usr/local/bin/vboxmanage modifyvm ' + vm_name +
                   ' --natpf1 delete \'' + port_name + '\'')
        results = host_ssh(user, command, timeout_in_secs)
        if results == 'CalledProcessError':
            return 'FAIL - Forwarding port could not be deleted.'
        if results == 'TimeoutError':
            return 'FAIL - Deletion of port forwarding rule took longer than \
        %f seconds' % timeout_in_secs
    else:
        try:
            results = subprocess.run(['VBoxManage', 'modifyvm', vm_name,
                                      '--natpf1', 'delete', port_name],
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     timeout=timeout_in_secs)
        except subprocess.CalledProcessError:
            return 'FAIL - Forwarding port could not be deleted.'
        except subprocess.TimeoutExpired:
            return 'FAIL - Deletion of port forwarding rule took longer than \
        %f seconds' % timeout_in_secs
    results = results.stdout.decode('utf-8')
    results = results.strip()
    return results


def create_port_forward_rule(user, vm_name, tcp_port, virtualized):
    '''
    Add port forwarding rule in virtual machine
    '''
    timeout_in_secs = 5

    if virtualized:
        command = ('/usr/local/bin/vboxmanage modifyvm ' + vm_name +
                   ' --natpf1 ' + f'ssh2,tcp,,{tcp_port},,22')
        results = host_ssh(user, command, timeout_in_secs)
        if results == 'CalledProcessError':
            return 'FAIL - Forwarding port could not be created.'
        if results == 'TimeoutError':
            return 'FAIL - Creation of port forwarding rule took longer than \
        %f seconds' % timeout_in_secs
    else:
        try:
            results = subprocess.run(['VBoxManage', 'modifyvm',
                                      vm_name, '--natpf1',
                                      f'ssh2,tcp,,{tcp_port},,22'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return 'FAIL - Forwarding port rule could not be created.'
        except subprocess.TimeoutExpired:
            return 'FAIL - Creation of port forwarding rule took longer than \
        %f seconds' % timeout_in_secs
    results = results.stdout.decode('utf-8')
    results = results.strip()
    return results


def rename_vm(user, vm_name, new_vm_name, virtualized):
    '''
    Rename the virtual machine
    '''
    timeout_in_secs = 60

    if virtualized:
        command = ('/usr/local/bin/vboxmanage modifyvm '
                   + vm_name + ' --name ' + new_vm_name)
        results = host_ssh(user, command, timeout_in_secs)
        if results == 'CalledProcessError':
            return 'FAIL - Virtual machine could not be renamed.'
        if results == 'TimeoutError':
            return 'FAIL - VM rename operation took longer than %f \
        seconds' % timeout_in_secs
    else:
        try:
            subprocess.run(['VBoxManage', 'modifyvm',
                            vm_name, '--name', new_vm_name],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           timeout=timeout_in_secs)
        except subprocess.CalledProcessError:
            return 'FAIL - Virtual machine could not be renamed.'
        except subprocess.TimeoutExpired:
            return 'FAIL - VM rename operation took longer than %f \
                seconds' % timeout_in_secs
    return 'SUCCESS - Virtual machine successfully renamed.'


def start_vm(user, vm_name, virtualized):
    '''
    Start the virtual machine.
    '''
    timeout_in_secs = 60

    vms = list_vms(user, virtualized)

    if vm_name in vms:
        if virtualized:
            command = ('/usr/local/bin/vboxmanage startvm --type headless '
                       + vm_name)
            results = host_ssh(user, command, timeout_in_secs)
            if results == 'CalledProcessError':
                return 'FAIL - Virtual machine could not be started.'
            if results == 'TimeoutError':
                return 'FAIL - VM startup took longer than %f \
                seconds' % timeout_in_secs
        else:
            try:
                subprocess.run(['VBoxManage', 'startvm',
                                '--type', 'headless',
                                vm_name],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               timeout=timeout_in_secs)
            except subprocess.CalledProcessError:
                return 'FAIL - Virtual machine could not be started.'
            except subprocess.TimeoutExpired:
                return 'FAIL - VM startup took longer than %f \
                seconds' % timeout_in_secs
        while ((vm_name not in list_running_vms(user, virtualized)) and
               timeout_in_secs > 0):
            time.sleep(1)
            timeout_in_secs -= 1
            if timeout_in_secs == 0:
                return 'FAIL - Virtual machine could not be started.'
        return 'SUCCESS - Virtual machine successfully started.'
    else:
        return 'FAIL - Virtual machine not found'


def stop_vm(user, vm_name, virtualized):
    '''
    Shutdown the virtual machine.
    '''
    timeout_in_secs = 60

    vbox_path = utils.VMS_VBOXMANAGE_PATH

    running_vms = list_running_vms(user, virtualized)

    if vm_name in running_vms:
        if virtualized:
            stop_command = vbox_path + ' controlvm ' + vm_name + ' poweroff'
            results = host_ssh(user, stop_command, timeout_in_secs)
            if results == 'CalledProcessError':
                return 'FAIL - Virtual machine could not be shutdown.'
            if results == 'TimeoutError':
                return 'FAIL - VM shutdown took longer than %f \
                seconds' % timeout_in_secs
        else:
            try:
                subprocess.run(['VBoxManage', 'controlvm',
                                vm_name, 'poweroff'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               timeout=timeout_in_secs)
            except subprocess.CalledProcessError:
                return 'FAIL - Virtual machine could not be shutdown.'
            except subprocess.TimeoutExpired:
                return 'FAIL - VM shutdown took longer than %f \
                seconds' % timeout_in_secs
        while ((vm_name in list_running_vms(user, virtualized)) and
               timeout_in_secs > 0):
            time.sleep(1)
            timeout_in_secs -= 1
            if timeout_in_secs == 0:
                return 'FAIL - Virtual machine could not be shutdown.'
        return 'SUCCESS - Virtual machine successfully shutdown.'
    else:
        return 'SUCCESS - Virtual machine already shutdown'


def delete_vm(user, vm_name, virtualized):
    '''
    Deletes the virtual machine -- this is a hard delete where all the virtual
    machine files (e.g., .vdi, .vbox) are completely removed
    '''
    timeout_in_secs = 60

    vbox = utils.VMS_VBOXMANAGE_PATH

    registered_vms = list_vms(user, virtualized)

    if vm_name in registered_vms:
        if virtualized:
            delete_command = vbox + ' unregistervm ' + vm_name + ' --delete'
            results = host_ssh(user, delete_command, timeout_in_secs)
            if results == 'CalledProcessError':
                return 'FAIL - Virtual machine could not be deleted.'
            if results == 'TimeoutError':
                return 'FAIL - VM deletion took longer than %f \
                seconds' % timeout_in_secs
        else:
            try:
                subprocess.run(['VBoxManage', 'unregistervm',
                                vm_name, '--delete'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               timeout=timeout_in_secs)
            except subprocess.CalledProcessError:
                return 'FAIL - Virtual machine could not be deleted.'
            except subprocess.TimeoutExpired:
                return 'FAIL - VM deletion took longer than %f \
                seconds' % timeout_in_secs
        while ((vm_name in list_vms(user, virtualized)) and
               timeout_in_secs > 0):
            time.sleep(1)
            timeout_in_secs -= 1
            if timeout_in_secs == 0:
                return 'FAIL - Virtual machine could not be deleted.'
    return 'SUCCESS - Virtual machine successfully deleted.'

def delete_vm_group(user, vm_name, virtualized):
    '''
    Delete groups from virtual machine
    '''
    timeout_in_secs = 5

    if virtualized:
        command = ('/usr/local/bin/vboxmanage modifyvm ' + vm_name +
                   ' --groups ""')
        results = host_ssh(user, command, timeout_in_secs)
        if results == 'CalledProcessError':
            return 'FAIL - VM group could not be deleted.'
        if results == 'TimeoutError':
            return 'FAIL - Deletion of VM group took longer than \
        %f seconds' % timeout_in_secs
    else:
        try:
            results = subprocess.run('VBoxManage modifyvm ' + vm_name +
                                      ' --groups ""', shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     timeout=timeout_in_secs)
        except subprocess.CalledProcessError:
            return 'FAIL - VM group could not be deleted.'
        except subprocess.TimeoutExpired:
            return 'FAIL - Deletion of VM group took longer than \
        %f seconds' % timeout_in_secs
    results = results.stdout.decode('utf-8')
    results = results.strip()
    return results


if __name__ == '__main__':
    pass
