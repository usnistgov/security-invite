#!/usr/bin/env python3
""" The module aggregates utility providing functions and classes for
    repeatable environment-specific operations such
# =============================================================================
    This software was developed at the National Institute of Standards
    and Technology by employees of the Federal Government in the course
    of their official duties.  Pursuant to title 17 Section 105 of the
    United States Code this software is not subject to copyright
    protection and is in the public domain.  NIST assumes no
    responsibility whatsoever for its use by other parties, and makes
    no guarantees, expressed or implied, about its quality,
    reliability, or any other characteristic.
# =============================================================================
    We would appreciate acknowledgement if the software is used.
"""
# Py-Linter setup for f'string' format:
# logging-format-style=fstr
__author__ = "Dmitry Cousin"
__status__ = "Prototype"

import os
import sys
import argparse
import fcntl
import fileinput
import logging
import re
import subprocess
import socket
from enum import Enum

from pathlib import Path
from datetime import datetime
# import si_server_vm_manage as vmmanage


def get_timestamp() -> str:
    """ Returns file-name-safe timestamp string in ISO-like format
        (Has to be here for constants to use it)
    """
    # ts = str(datetime.datetime.now()).replace(' ', '_').replace(':', '=').replace(',', '-')
    time_stamp = datetime.now().strftime("%Y-%m-%d-@-%Ih-%Mm-%Ss-%fms-%p")
    return time_stamp

_TIME_STAMP = get_timestamp()
_SI_HOME = '/security-invite'
_USER_HOME = str(Path.home())
_IS_HARDWARE = False    # Use this flag to force hardware logic
_MACOS_SI_DIR = f'{_USER_HOME}{_SI_HOME}'
_Sec_InVITE_HOME = (_SI_HOME if (_IS_HARDWARE or 'tciadmin' in _USER_HOME)
                   else f'{_USER_HOME}{_SI_HOME}')

# Variables containing paths existing on the macOS Intel laptops.
MACOS_ISO_PATH = os.path.join(_MACOS_SI_DIR, 'share', 'autoinstall.iso')
MACOS_KNOWN_HOSTS_PATH = os.path.join(_USER_HOME, '.ssh', 'known_hosts')
MACOS_OVA_DIR = os.path.join(_MACOS_SI_DIR, 'ova')
MACOS_OVA_DIR_FROM_SI = f'~{_SI_HOME}/ova'
MACOS_RESULTS_DIR = os.path.join(_MACOS_SI_DIR, 'results')
MACOS_VBOX_DIR = os.path.join(_MACOS_SI_DIR, 'vbox_dir')
MACOS_VBOX_DIR_FROM_SI = f'~{_SI_HOME}/vbox_dir'
MACOS_SETUP_KEY_PATH = os.path.join(_MACOS_SI_DIR, 'ssh_keys', 'setup.pri')
MACOS_SSH_KEYS_DIR = os.path.join(_MACOS_SI_DIR, 'ssh_keys')
MACOS_SI_DIR = os.path.join(_MACOS_SI_DIR, 'tci')
MACOS_Sec_InVITE_DIR = _MACOS_SI_DIR

# Variables used by scripts running only on the VMServer (Hardware and Virtual).
VMS_HELLOVM_LOG_PATH = f'{_SI_HOME}/logs/hellovm.log'
VMS_STAGING_DIR = f'{_SI_HOME}/staging'
VMS_SUBMISSION_PORT_PATH = f'{_SI_HOME}/config/submission_port'

def get_fresh_timestamped_log(server_name: str = 'echo_server'):
    """ Refreshes timestamp used for log, input, and other timestamped files
    """
    global _TIME_STAMP, VMS_TEST_LOG_PATH
    _TIME_STAMP = get_timestamp()
    VMS_TEST_LOG_PATH = f'{_Sec_InVITE_HOME}/logs/test-{server_name}-on-{_TIME_STAMP}.log'
    return VMS_TEST_LOG_PATH

VMS_TEST_HOMEWORK_LOG_PATH = f'{_Sec_InVITE_HOME}/logs/test-HOMEWORK-on-{_TIME_STAMP}.log'
VMS_TEST_ECHO_LOG_PATH = f'{_Sec_InVITE_HOME}/logs/test-HW_server-on-{_TIME_STAMP}.log'

# Variables used by scripts running only on the VMServer (Hardware).
VMS_HW_KEY_PATH = f'{_SI_HOME}/ssh_keys/hw.pri'
VMS_VBOXMANAGE_PATH = 'VBoxManage' # Use environment to determine
VMS_OVA_DIR = f'{_SI_HOME}/ova'

# Variables used by scripts running only on the VMServer (Virtual).
VMS_VIRTUAL_OVA_DIR = '/media/sf_security-invite/ova'
VMS_VIRTUAL_VBOX_DIR = '/media/sf_security-invite/vbox_dir'

# Variables used by scripts running on both TCServer and the VMServer (Hardware and Virtual).
SI_Sec_InVITE_DIR = f'{_SI_HOME}'
SI_ADMIN_DIR = f'{_SI_HOME}/tciadmin'
SI_ADMIN_HOME = '/home/tciadmin'
SI_SSH_KNOWN_HOSTS = f'{SI_ADMIN_HOME}/.ssh/known_hosts'


# Variables used during validation of virtual machines during import

MAX_MEMORY = 4096
MAX_CPUS = 2
MAX_VRAM = 128

# Variables used generically, e.g., on macOS and on the TCServer.
SETUP_KEY_PATH = f'{_SI_HOME}/ssh_keys/setup.pri'
SSH_KEYS_DIR = f'{_SI_HOME}/ssh_keys'
SI_CONF_PATH = f'{_SI_HOME}/ssh_keys/tci.conf'

# File extensions.
FAIL = 'FAIL'
PART = 'PART'
RESULTS = 'RESULTS'
RUN = 'RUN'
SUCCESS = 'SUCCESS'

# Fully-specified DNS names of servers.
TCSERVER = 'tcserver.tc.nist.gov'
VMSERVER = 'vmserver.tc.nist.gov'

# IP addresses
TCSERVER_IP = '192.168.0.1'
MACOS_IP = '192.168.0.5'

# Reconfigurable administrative user.
ROOT = 'tciadmin'

class SynchronizedFile():
    """Context manager for reading/writing files exclusively using 'with'."""
    def __init__(self, path):
        self.path = path
        self.open_file = ''
        self.open_fd = ''

    def __enter__(self):
        self.open_file = open(self.path, 'r+')
        self.open_fd = self.open_file.fileno()
        fcntl.lockf(self.open_fd, fcntl.LOCK_EX)
        return self.open_file

    def __exit__(self, *args):
        fcntl.lockf(self.open_fd, fcntl.LOCK_UN)
        self.open_file.close()


class SignalHandler():
    """ Sets and returns the state of the kill_signal. """

    def __init__(self):
        self.kill_signal = 0
        self.signum = 0
        self.frame = ""

    def set_handler_to_one(self, signum, frame):
        """ Sets the kill_signal to 1. This function is
        intended to be called by a signal """
        self.kill_signal = 1
        self.signum = signum
        self.frame = frame

    def handler_reset(self):
        """ Sets the kill_signal to 0."""
        self.kill_signal = 0
        self.signum = 0
        self.frame = ""

    def get_signal(self):
        """ returns kill_signal."""
        return self.kill_signal


def server_ssh(ip_address, command):
    """Run the passed command as root on the server at ip_address.

    The use of raw IP addresses allow this code to work prior to DNS.
    Returns the string from the command's execution on the server.
    Assumes the server is up. TBD fix.
    Assumes that the file setup.pri .key is in the current dir. TBD fix.
    """
    result = subprocess.run(['ssh',
                             ROOT + '@' + ip_address,
                             '-i', SETUP_KEY_PATH,
                             '-o', 'IdentitiesOnly=yes',
                             '-o', 'StrictHostKeyChecking=no',
                             '-q',
                             command],
                            timeout=10.0,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    output_string = result.stdout.decode('utf-8')
    return output_string.strip()


def server_ssh(command):
    """Run the passed command as root on the teserver."""
    return server_ssh('192.168.0.1', command)


def confirm_running_as_root_on_ubuntu_linux():
    """Exit the program if we are not running as root on Ubuntu Linux."""
    if os.getuid():
        print('This script requires root privilege, exiting...')
        sys.exit()
    os_identity = os.uname()
    os_identity_matches_ubuntu = [x for x in os_identity if 'Ubuntu' in x]
    if not os_identity_matches_ubuntu:
        print('This script must be run on Ubuntu Linux, exiting...')
        sys.exit()


def create_diagnostic_logger(logger_name, log_file_name, log_level):
    """Diagnostic logger configuration: log to a file AND to the console."""
    #print(f'Name={logger_name}, File={log_file_name}, Level={log_level}')
    diagnostic_logger = logging.getLogger(logger_name)

    datetime_format_ISO = '%Y-%m-%dT%H:%M:%S%z'
    NEW_LOG_FORMAT = (  
                    f'\n\n!!!{"="*80}\n!!!=> %(asctime)s \n'
                    f'\tLogged by: %(name)s\t@Level: %(levelname)s:\n'
                    f'\tIn function: [%(funcName)s]\t@Line No: %(lineno)d\n'
                    f'\t%(message)s\n!!!{"="*80}')
    # Old one-line format
    # '%(asctime)s.%(msecs)03d %(message)s',
    formatter = logging.Formatter(
            fmt = NEW_LOG_FORMAT,
            datefmt=datetime_format_ISO)

    file_handler = logging.FileHandler(log_file_name, mode='a')
    file_handler.setFormatter(formatter)    
    # file_handler.setLevel(log_level)
    diagnostic_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()

    # console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    diagnostic_logger.addHandler(console_handler)
    diagnostic_logger.setLevel(log_level)

    diagnostic_log = logging.getLogger(logger_name)
    diagnostic_log.critical(f'created logger {logger_name} in file {log_file_name} with level: {log_level}')
    return diagnostic_log

def delete_ssh_known_host_entries_for_address(known_hosts_path, address):
    """Remove all entries from the SSH known hosts file that match address."""
    for line in fileinput.input(known_hosts_path, inplace=True):
        if not re.search(address, line):
            print(line, end='')


def get_next_unused_local_tcp_port():
    """Return the next available (unused) TCP port on the local host."""
    # Credit: adapted from: https://unix.stackexchange.com/questions
    # /55913/whats-the-easiest-way-to-find-an-unused-local-port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    addr = sock.getsockname()
    free_port = addr[1]
    sock.close()
    return free_port



class AppToExecute(Enum):
    """ The application defaults
    """
    NOOP = ('', '', '', False)
    ECHO = ('echo_server', './echo_server', 'Echo_Logs', False)
    MAIN = ('atm', './atm', 'Main_Logs', True)
    
    SI_HW1 = ('hw1', 'python3 ./hw1.py', 'HW1_Logs', True)
    SI_HW2 = ('hw2', 'python3 ./hw2.py', 'HW2_Logs', True)
    SI_HW3 = ('hw3', 'python3 ./hw3.py', 'HW3_Logs', True)
    SI_HW4 = ('hw4', 'python3 ./hw4.py', 'HW4_Logs', True)
    SI_HW5 = ('hw5', 'python3 ./hw5.py', 'HW5_Logs', True)
    SI_HW6 = ('hw6', 'python3 ./hw6.py', 'HW6_Logs', True)

    def __init__(self, bare_name: str, app_to_run: str, log_dir: str, deep_test: bool):
        self._bare_name = bare_name  # bare app name to run
        self._app_to_run= app_to_run      # default app to Run
        self._log_dir = log_dir      # default log Dir
        self._deep_test = deep_test  # default for deep testing

    @property
    def app(self) -> str:
        """ Returns name of the default App to run """
        return self._app_to_run

    @property
    def log_dir(self) -> str:
        """ Returns name of the default log directory for App """
        return self._log_dir

    @property
    def is_deep_test(self) -> bool:
        """ Returns deep test mode BOOLEAN flag"""
        return self._deep_test

    @property
    def bare_name(self) -> bool:
        """ Bare App name """
        return self._bare_name


def ensure_dir(file_path):
    """ Ensures that the directory-path exists with os tools (at least on Linux)
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_fresh_timestamped_log(server: AppToExecute, subdir='logs', ext='.log') -> str:
    """ Refreshes timestamp used for log, input, and other timestamped files
    """
    global _TIME_STAMP, VMS_TEST_LOG_PATH
    log_dir_name = server.log_dir
    server_name = server.bare_name
    _TIME_STAMP = get_timestamp()
    VMS_TEST_LOG_PATH = f'{_Sec_InVITE_HOME}/{subdir}/{log_dir_name}/test-{server_name}-on-{_TIME_STAMP}{ext}'
    ensure_dir(VMS_TEST_LOG_PATH)
    return VMS_TEST_LOG_PATH


def saved_json_test_report_ok(json_file, result) -> str:
    """ Records the test results as JSON output
    """
    # print(f'Saving JSON-results to {json_file}\n IsFile {os.path.isfile(json_file)}\n ExistsPath {os.path.exists(os.path.dirname(json_file))}')
    try:
        if (os.path.exists(os.path.dirname(json_file)) and not os.path.isfile(json_file)):
            json_string = json.dumps(result.test_results, indent=1)
            # print(json_string)
            with open(json_file, 'w') as json_data:
                json_data.write(json_string)
        return None
    except Exception as ex:
        # print(f'Failed saving JSON-results to {json_file}\n Exception {ex}')
        return str(ex)


def delete_ssh_known_host_entries_for_address(known_hosts_path, address):
    """Remove all entries from the SSH known hosts file that match address."""
    for line in fileinput.input(known_hosts_path, inplace=True):
        if not re.search(address, line):
            print(line, end='')



class VmTestArguments(object):
    """ Class wraps around the command line parameters into the
        set of "smart" properties that can be used by both test sets
    """

    def __init__(self,
                 port_file_name: str = '/toolchain/config/submission_port',
                 default_user: str = 'toolchain', 
                 app_defaults:AppToExecute = AppToExecute.NOOP,
                 ):
        
        self.app_defaults = app_defaults
        self.port_file_name = port_file_name
        self.default_user = default_user
        self.__app_to_execute = None
        self.__skip_deep_test = None
        self.__eol_break_replace = None
        self.__log_file_name = None
        self.__json_file_name = None
        self.__logger_name = None
        self.__logger = None
        self.__args = None
        self.__bare_app_name = self.app_defaults.bare_name
        # Scoring DB configuration
        self.__score_db_file_name = None
        self.__score_db_dir_name = None
        self.__vm_name = None
        self.__app_to_run=''

        parser = argparse.ArgumentParser(description='Test an echo_server ' +
                                         'by invoking it over SSH.')


        parser.add_argument('-u', '--User', action='store', dest='user_name',
                            default='',
                            help=("The USER-NAME in your VM you want to run the tests under and have SSH configured for")
                            ,required=True
                            )

        parser.add_argument('-hw', '--Homework#', metavar='Homework#',
                            action="store", choices=range(1,6),
                            default='1', type=int,
                            dest='homework_number',
                            help="Homework number to test in VM. (Can replace -r option)")

        parser.add_argument('-r', metavar='app_to_run', action="store",
                            dest='app_to_run',
                            default=self.app_defaults.app,
                            help='The application to start on VM' +
                            '(.\\echo_server, ./echo_server, ~/echo_server, etc).' +
                            ' Default is ./echo_server')

        parser.add_argument('-a', action='store', dest='address', metavar='address',
                            default='',
                            help=("IP address of VM where the echo_server program" +
                                  " is installed. Should default to localhost " +
                                  " or 127.0.0.1"))
        
        parser.add_argument('-k', metavar='key_file', action='store',
                            dest='key_file', default='',
                            help='The key to use for ssh authentication.')
        
        parser.add_argument('-t', metavar='test_vm', action="store",
                            dest='test_vm', default='',
                            help=("Name of the VM where the tested program is installed."))
        
        parser.add_argument('-f', metavar='file_name', action="store",
                            dest='file_name', default='',
                            help="File in which to write test report." +
                            " If no file_name is given, output is " +
                            "sent to the standard output stream.")

        parser.add_argument('-w', metavar='port_forwarding', action='store',
                            type=int, dest='port_forwarding', default='2020',
                            help=('The port on VM that was redirected to '
                                  'ssh-port 22 (defaults to 2020).'))
        
        parser.add_argument('-b', metavar='breaks_for_eol', action='store',
                            type=str, dest='breaks_for_eol', default='',
                            help=('The line break character that needs to be replaced'                                  
                            ' for the platform. Use as -b "\\r,\\r\\n"'))

        
        parser.add_argument('-d', '--deep_test', action="store",
                            default='1111',
                            dest='deep_test',
                            help="The tests depth to run on VM.")
        
        parser.add_argument('--logger', metavar='MODE', action="store",
                            dest='level', default='INFO',
                            choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO',
                                     'DEBUG', 'NOTSET'],
                            help='Set the log level, MODE must be "CRITICAL, '
                                 '"ERROR", "WARNING", "INFO", "DEBUG", '
                                 'or "NOTSET"')
        # TODO: Not hurting anything, but does not help either
        parser.add_argument('-rr', metavar='remote_remove', action='store',
                            type=str, dest='remote_remove', default='rm',
                            help='Remote remove command remote OS expects.\n' +
                            ' Default is rm, which works on both Linux and Windows-PowerShell.\n' +
                            ' Ideally, for Linux -rr should be set to "rm -rf, while for\n"' +
                            ' Windows should set it to "del" in CMD context or "rm" in PowerShell')   
             
        # TODO: Possibly remove
        parser.add_argument('--path', '-p', metavar='keys_path', dest='keys_path',
                            type=str, default='/toolchain/ssh_keys/',
                            help='Path to the keys file ending with slash. E.g. /toolchain/ssh_keys/')
        args = parser.parse_args()
        self.__args = args
        self.set_defaults()
        # Option for flipping deep tests
        self.__skip_deep_test = self.__args.deep_test

        # Debugging the line end brake to figure out how to feed EOL
        # into the parameters from Windows and Linux command line
        self.__replace_eol_break = self.__args.breaks_for_eol
        if self.__replace_eol_break:
            # print(self.__replace_eol_break)
            sss = self.__replace_eol_break.split(',')
            for s in sss:
                if s == '\\n':
                    # print('L-Br C-Style')
                    pass
                if s == '\\r':
                    # print('Old-Apple-Style Line Break')
                    pass
                if s == '\\r\\n':
                    # print('Java-on-Win-Style Line Break')
                    pass
                else:
                    # print(f"Unknown line-break! {[ord(z) for z in s ]}")
                    pass
            sys.exit(10)

    def set_defaults(self):
        if self.homework_number == 1: 
            self.app_defaults = AppToExecute.SI_HW1
        elif self.homework_number == 2: 
            self.app_defaults = AppToExecute.SI_HW2
        elif self.homework_number ==3: 
            self.app_defaults = AppToExecute.SI_HW3
        elif self.homework_number == 4: 
            self.app_defaults = AppToExecute.SI_HW4
        elif self.homework_number == 5: 
            self.app_defaults = AppToExecute.SI_HW5
        elif self.homework_number == 6: 
            self.app_defaults = AppToExecute.SI_HW6
        self.__app_to_run = (f'python3 hw{self.homework_number}.py' 
                             if not self.__args.app_to_run
                             else self.__args.app_to_run.strip()
                             )

    @property
    def ssh_address(self):
        ret_val = self.__args.address if self.__args.address else 'localhost'
        return ret_val

    @property
    def app_to_execute(self)-> AppToExecute:
        self.app_defaults

    @property
    def app_args(self) -> argparse.Namespace:
        return self.__args
    
    @property
    def homework_number(self)->int:
        if self.__args.homework_number and self.__args.homework_number in range(1,6):
            return self.__args.homework_number
        return -1

    @property
    def score_db_file_name(self) -> str:
        """ Returns EoL break or breaks specific to a platform
        """
        if not self.__score_db_file_name:
            db_name = 'Scores'
            self.__score_db_file_name = f'{db_name}'
        return self.__score_db_file_name

    @property
    def score_db_dir_name(self) -> str:
        if not self.__score_db_dir_name:
            work_dir = Path(Path.home(), 'tci-scores')
            if not Path.exists(work_dir):
                os.makedirs(work_dir)
            self.__score_db_dir_name = work_dir
        return self.__score_db_dir_name

    @property
    def score_vm_name(self) -> str:
        if not self.__vm_name:
            target_vm = self.__args.test_vm
            self.__vm_name = target_vm
        return self.__vm_name

    @ property
    def logger_file_name(self):
        """ Returns EoL break or breaks specific to a platform
        """
        if not self.__log_file_name:
            self.__log_file_name = get_fresh_timestamped_log(self.app_defaults)
        return self.__log_file_name

    @ property
    def json_file_name(self):
        """ Returns EoL break or breaks specific to a platform
        """
        if not self.__json_file_name:
            self.__json_file_name = get_fresh_timestamped_log(
                self.app_defaults, 'results', '.json')
        return self.__json_file_name

    @ property
    def logger(self):
        """ Returns logger
        """
        if not self.__logger:
            self.__logger_name = f'{self.__bare_app_name}@{self.app_defaults.log_dir}'
            self.__logger = create_diagnostic_logger(self.__logger_name,
                                                     self.logger_file_name,
                                                     self.logging_level)
        self.__logger.debug(f'Log {self.__logger_name} will be located at the following path:'
                            f'{self.logger_file_name} at {self.logging_level} level.')
        return self.__logger

    @ property
    def eol_breaks_to_replace(self):
        """ Returns EoL break or breaks specific to a platform
        """
        return self.__replace_eol_break

    @ property
    def key_file_path(self) -> str:
        """ Makes decision on the way the key file name is built
            if parameter -t was provided it takes priority
            otherwise self.skip_deep_test -k
            if neither was found None comes back
        """
        # init all pertinent member-variables
        key_file = self.__args.key_file
        keys_path = self.__args.keys_path
        self.__vm_name = self.__args.test_vm
        vm_key_name = self.__vm_name[2:-2]+'vm_pri'
        # print(f'Key_file:{key_file}\nKeys_path:{keys_path}\nVM Key Name:{vm_key_name}')
        # Assign initial state to the key file resolution variables
        return_value = None
        if keys_path and self.__vm_name:
            return_value = keys_path + vm_key_name
        elif key_file:
            return_value = key_file  # e.g. '/Users/dummy/.ssh/id_rsa_LEG'
        print(f'Key file is resolved to {return_value}')
        return return_value

    @ property
    def user_at_address(self) -> str:
        """ Produces the username for SSH login
        :return: The username at VM address (e.g. toolchain@localhost)
        """
        user_name = ''
        if self.__args.user_name:
            user_name = self.__args.user_name        
        host_address = user_name if user_name.endswith('@') else f'{user_name}@localhost'
        if not len(user_name)>0:
            print(f"\n\t!!! You did not specify mandatory user name.\n\tPlease add parameter:\n\t-u <si_vm_user_name> \n\tor\n\t-User <si_vm_user_name>\n\tto test_homework.py call that specifies the user name you have set up in VM!!!\n")
            sys.exit(0)
        return host_address

    @ property
    def tcp_port(self) -> str:
        """
        :return: The port nubmer as STR otherwise it blows array
        """
        file_port = None
        port_file_name = self.port_file_name
        if os.path.isfile(self.port_file_name):
            port_file = open(port_file_name, 'r')
            file_port = str.strip(port_file.readline())
        param_port = str(self.__args.port_forwarding)
        if param_port == '2020' and file_port:
            return file_port
        return param_port

    @ property
    def app_to_run(self) -> str:
        """ Specifies fully invocable path-to-run for the application
        :return: the string
        """
        # The app to run can be specified in -r parameter (defaults to None)
        if self.__app_to_run:
            return self.__app_to_run
        else:
            return_value = f"./{self.__bare_app_name}"
            if self.__args.app_to_run:
                return_value = str.strip(self.__args.app_to_run)
            elif self.__args.homework_number and self.__args.homework_number in range(1, 6) :
                return_value = f'python3 hw{self.__args.homework_number}.py'
                return 
            return return_value

    @ property
    def deep_test_level(self) -> int:
        """ Reruns integer level of deep tests to run
        :return: INT! to
        """
        deep_test = str.strip(self.__args.deep_test)
        try:
            try:
                # in case arg was integer parsable
                return int(deep_test, base=10)
            except ValueError:
                # in case we can parse it as float
                return int(float(deep_test), base=10)
        except ValueError:
            return -1  # The default value for imparsable inputs

    @ property
    def do_deep_tests(self) -> bool:
        """ Reruns BOOL FLAG
        :return: SKIP (False) deep tests or NOT (True)
        """
        level = self.deep_test_level
        flag = False
        if self.app_defaults == AppToExecute.MAIN:
            flag = level > 40
        if self.app_defaults == AppToExecute.ECHO:
            flag = level > 10
        return flag

    @ property
    def keys_path(self) -> str:
        """ Returns keys path verbatim from the command Arguments
        """
        return self.__args.keys_path

    @ property
    def logging_level(self) -> str:
        """ Returns the log Level/Mode from arguments verbatim
        """
        return self.__args.level

    @ property
    def remote_remove_command(self) -> str:
        """ Returns the remote return command such as 'rm', 'rm -rf', or 'del'
        """
        return self.__args.remote_remove

    @ property
    def report_file_name(self) -> str:
        """ Returns the log Level/Mode from arguments verbatim
        """
        return self.__args.file_name


if __name__ == "__main__":
    # my_args = VmTestArguments("./mySelf")
    # print(f"Key File Path: {my_args.key_file_path}")
    # print(f"App to Run: {my_args.app_to_run}")
    # print(f"Skip Deep Test: {my_args.skip_deep_tests}")
    # print(f"TCP Port #: {my_args.tcp_port}")
    # print(f"USer @ Address: {my_args.user_at_address}")
    # print(f"EOL Breaks Collection: {my_args.eol_breaks_to_replace}")
    # print(f"Keys Path: {my_args.keys_path}")
    # print(f"Logs Mode: {my_args.logging_level}")
    # print(f"Logs Mode: {my_args.report_file_name}")
    pass