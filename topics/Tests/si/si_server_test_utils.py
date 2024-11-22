#!/usr/bin/env python3
""" The module aggregates ultility providing functions and classes for
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
__author__ = "Dmitry Cousin"
__status__ = "Prototype"

from datetime import datetime
import time
import os
import re
import sys
import select
import subprocess
import unittest
from enum import IntEnum
import traceback
import unittest.case
# import si_server_vm_manage as vmmanage


THIS_MODULE = sys.modules[__name__]
THIS_MODULE.TEST_STATUS = None
# Limit how much data we will accept from the
# program under test. Arbitrarily limit to 10MB.
# Protect this program from accidental-or-intentional
# over-production of data by the tested program.
THIS_MODULE.DATA_LENGTH = 10000000

def get_test_status():
    """ Returns test results object accumulated in the module level variable
    """
    return THIS_MODULE.TEST_STATUS

def get_location(level: int = 1) -> str:
    """ Gets location description for the call place to log exact function name, file, and line
    """
    locator = sys._getframe(1) # elevate in stack to the previous position (the caller)
    return (f' func: {locator.f_code.co_name}'
            f' at line: {locator.f_lineno}'
            f' of file: {locator.f_code.co_filename} ')


class ServerSI(object):
    """ ServerSI Aggregates common server operations necessary for homework testing
    """
    def __init__(self,
                 app_to_test: str,
                 host_address: str, tcp_port: str, key_file: str,
                 logger,
                 remote_remove_command: str = 'rm -rf ',
                 wait_on_stop: float = 2.0):
        """ Initializes set of common operations for the testing suites
        """
        self.timeout = 1000
        self.app_to_test = app_to_test
        self.host_address = host_address
        self.tcp_port = tcp_port
        self.key_file_path = key_file
        self.logger = logger
        self.log_level = self.logger.getEffectiveLevel()
        self.wait_limit = wait_on_stop  # seconds we are willing to wait for process shutdown

        self.remove_command = remote_remove_command
        self.ssh_params = \
           ['ssh', self.host_address,
            '-p', self.tcp_port,
            '-i', self.key_file_path,
            '-o', 'StrictHostKeyChecking=no', '-q']
        self.ssh_params_ext = \
           ['ssh', self.host_address,
            '-p', self.tcp_port,
            '-i', self.key_file_path,
            '-o', 'StrictHostKeyChecking=no', '-q']
        self.scp_params = \
           ['scp', #'-v',
            '-P', self.tcp_port, # Important!!! Capital P for SCP unlike for SSH
            '-i', self.key_file_path,
            '-o', 'StrictHostKeyChecking=no']
    #----------------------------------------------------------------------------

    def verify_recreate_test_tree(self):
        paths=[
            os.path.expanduser("~/si"),
            os.path.expanduser("~/si/log"),
            os.path.expanduser("~/si/db"),
            os.path.expanduser("~/si/set"),
        ]
        for dir in paths:
            if not os.path.isdir(dir):
                os.makedirs(dir)
                print(f"\n\tCreated path '{dir}'")
    #----------------------------------------------------------------------------

    def list_add(self, source: list, extra: list) -> list:
        """ Compact wrap-around made for array extension and manipulation
        """
        add_result = source.copy()
        add_result.extend(extra)
        return add_result
    # -------------------------------------------------------------------------

    def push_remote_file(self, config_file_name, config_file_contents):
        """Replaces the remote config file with new contents.

        This function uses the scp program to copy the new config file to
        a participant's host, even if the participant's host is the
        localhost (which will be the case for informal testing during
        development). To prevent confusion, the function creates first
        'local_conf' and then uses scp to copy that file to the "remote"
        host (so we don't overwrite the config file while reading from
        it).

        TBD: make sure documentation is clear about TCI having the rights
        to create files in the participant's home directory.
        """
        self.logger.debug(get_location())
        ssh_remove_old = self.list_add(self.ssh_params_ext, [self.remove_command, config_file_name])
        scp_command = self.list_add(self.scp_params,
                                    ['local_conf', f'{self.host_address}:{config_file_name}'])
        try:
            subprocess.call(ssh_remove_old)
            self.logger.debug(f'Done! Deleting remote file with:\n\t{ssh_remove_old}')

            with open('local_conf', mode='w') as file_obj:
                file_obj.write(config_file_contents)
            self.logger.debug(f'Done! Creating local file containing:\n\t{config_file_contents}')

            subprocess.call(scp_command)
            self.logger.debug(f'Done! Creating remote file {scp_command}')

            os.remove('local_conf')
            self.logger.debug('Done! Killing local file')
        except:
            self.logger.debug('Failed to push remote file')
    # -------------------------------------------------------------------------

    def kill_remote_file(self, config_file_name):
        """Do 'rm -rf' via ssh on remote system to delete the config file."""
        kill_command = self.list_add(self.scp_params, [self.remove_command, config_file_name])
        subprocess.call(kill_command)
    # -------------------------------------------------------------------------

    def read_up_to(self, sub_proc, expected_response_endswith):
        """Reads from sub_proc, returning chars up to and including expected_resp...
        If expected_value doesn't exist after waiting 1000ms, return
        partial data.
        """
        self.logger.debug(get_location())
        response_data = ''
        while True:
            inputs = [sub_proc.stdout]  # a pipe
            outputs = []
            timeout = self.timeout # 3.0  # We need a method for deciding this magic value.
            read, _write, _except = select.select(inputs, outputs, inputs, timeout)
            if read:
                try:
                    input_pipe = read[0]
                    msg = os.read(input_pipe.fileno(), 1024)
                    if not msg:   # means that the socket got closed
                        self.logger.debug('read_up_to: socket-got-closed')
                        return response_data
                    response_data += msg.decode()

                    # Limit how much data we will accept from the
                    # program under test. Arbitrarily limit to 10MB.
                    # Protect this program from accidental-or-intentional
                    # over-production of data by the tested program.
                    if len(response_data) > THIS_MODULE.DATA_LENGTH:
                        self.logger.debug('read_up_to: returning BIG response_data')
                        return response_data

                    if response_data.endswith(expected_response_endswith):
                        self.logger.debug('read_up_to: returning expected_response_data')
                        return response_data
                except OSError:
                    self.logger.critical('OSError thrown!')
                    sys.exit(0)
            else:
                self.logger.critical(f'TIMEOUT({response_data}) '+
                                     f'EXPECTED({expected_response_endswith})')
                return response_data
    # -------------------------------------------------------------------------

    def reset_server(self, conf='conf'):
        """ Resets the server
        """
        try:
            ssh_reset = self.list_add(self.ssh_params_ext, [self.app_to_test, '-i' ,conf])
            subprocess.call(ssh_reset)
        except Exception as ex:
            self.fail(ex)
    # -------------------------------------------------------------------------

    def start_server_ext(self, conf='', expected_response_endswith=':') ->tuple:
        """ Run the tested_ext program in a child process using ssh.
        Args:
            conf (str, optional): _description_. Defaults to 'conf'.
            expected_response_endswith (str, optional): _description_. Defaults to ':'.
        Returns:
            Tuple(Process, Response): Process of SSH probe and Response Text if caught here
        """
        self.logger.debug(f'Starting --Ext-- Server')
        # host_address = 'toolchain@192.168.0.5' if vmmanage.is_virtualized() else self.host_address
        # 'toolchain@localhost' or 'toolchain@192.168.0.5'
        try:
            ssh_params = self.list_add(self.ssh_params_ext, [self.app_to_test, conf])
            proc = subprocess.Popen(ssh_params,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            self.logger.debug(f'SSH P-open (--ext--) returned OK'
                              f' with the following params:\n\t{ssh_params}')
            response = self.read_up_to(proc, expected_response_endswith)
            return (proc, response)
        except subprocess.CalledProcessError:
            self.logger.critical(f'SSH P-open (--ext--) of ssh returned'
                                 f' error using the following params:\n\t{ssh_params}')
            return 'CalledProcessError'
    # -------------------------------------------------------------------------

    def get_home_on_vm(self):
        """ Retrieve home directory from the VM """
        home_dir = ''
        self.logger.debug(get_location())
        ssh_pwd = self.list_add(
            ['ssh', self.host_address,
            '-p', self.tcp_port,
            '-i', self.key_file_path,
            '-o', 'StrictHostKeyChecking=no', '-q'],
            ['pwd']
            )   
        try:
            stdout, stderr  = subprocess.Popen(ssh_pwd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT
                                    ).communicate()
            home_dir = stdout.decode('utf-8')
        except subprocess.CalledProcessError:
            self.logger.critical('subprocess.Popen of ssh returned error!')
            return 'CalledProcessError'
        finally:
            return home_dir.strip()
    # -------------------------------------------------------------------------

    def type_to_server_ext(self, subproc, command, response_end=': '):
        """Type a command to the running server_ext program and return the response.

        Note: many responses should end with ': '.

        There are 2 important cases:
            1) we got the entire tested program response, ending in response_end.
            2) we got some (or none) of the tested program response either
            because the tested program was too slow or because it died.
        """
        # self.logger.debug(get_location())
        try:
            pipe_fd = subproc.stdin.fileno()
            os.write(pipe_fd, (command + '\n').encode())

            response = self.read_up_to(subproc, response_end)
            self.logger.debug('type_to_server_ext: got a response')
            return response
        except Exception as ex:
            print(ex)
            pass
    # -------------------------------------------------------------------------

    def type_to_server(self, sub_proc, command, response_end='\n'):
        """Type a command to the running echo_server program and return the
        response.

        There are 2 important cases:
            1) we got the entire tested program response, ending in response_end.
            2) we got some (or none) of the tested program response either
            because the tested program was too slow or because it died.
        """
        self.logger.debug(get_location())
        pipe_fd = sub_proc.stdin.fileno()
        os.write(pipe_fd, (command + '\n').encode())

        response = self.read_up_to(sub_proc, response_end)
        self.logger.debug('type_to_server: got a response')
        return response
    # -------------------------------------------------------------------------
    

    def report_test_results(self, results):
        """ Reports results of the testing
        """
        n_successes = len(
            [x for x in results.test_results if x['result'] == 'SUCCESS'])
        n_failures = len(
            [x for x in results.test_results if x['result'] == 'FAILURE'])
        n_errors = len(
            [x for x in results.test_results if x['result'] == 'ERROR'])
        n_tests = n_successes + n_failures + n_errors
        report_line = (f'Ran {n_tests} tests:\n {n_successes} successes,' +
                       f'\n {n_failures} failures,\n {n_errors} errors')
        print(report_line)
        for test_record in results.test_results:
            if test_record:
                test_report = test_record['result'] if test_record['result'] else '- No Result Status Found -'
                if test_record["test_name"]:
                    test_report += f': {test_record["test_name"]}'
                else:
                    test_report += f'- No Test Name Found -'
                test_report += ' => ' + \
                    (test_record['doc'] if test_record['doc']
                     else ' - No Test Doc Found -')
                print(test_report)
            else:
                print(' => - No Test Record Found -')
    # -------------------------------------------------------------------------

    def stop_server(self, sub_proc):
        """Stop the echo_server program.

        Note: the close() of stdin performed here basically sends EOF to
        the subprocess (the ssh client-side program running in the TCI),
        which should then close its socket with the server side sshd
        (which is running in the participant's VM), causing both endpoint
        ssh processes to exit gracefully.

        TBD. We should probably specify the exiting behavior in Echo/Server.md
        """
        self.logger.debug(get_location())
        try:
            start_time = time.time()
            self.logger.debug('Beginning of try: in stop_server')
            if sub_proc:
                sub_proc.stdin.close()
                sub_proc.stdout.close()
                self.logger.debug('stop_server: before loop')
    
                while sub_proc.returncode is None:
                    time.sleep(0.1)  # keep from spinning too fast
                    if time.time() > start_time + self.wait_limit:
                        sub_proc.kill()
                        break
                    sub_proc.poll()
            self.logger.debug('stop_server: after loop')
        except Exception as ex:

            self.logger.exception(f'stop_server: exception {ex}',  exc_info=True)
            pass
            # If a test calls stop_echo_server() with an invalid
            # "subproc" parameter, which could happen with a few
            # complex tests, stop_ext() simply tolerates the lack of
            # initialization without crashing.
    # -------------------------------------------------------------------------

    def delete_file_on_vm(self, remote_file_name):
        """ Removes remote file """
        self.logger.debug(get_location())
        subprocess.call(['ssh', self.host_address,
                         '-p', self.tcp_port,
                         '-i', self.key_file_path,
                         '-o', 'StrictHostKeyChecking=no',
                         '-q', 'rm', remote_file_name])
    # -------------------------------------------------------------------------

    def copy_file_to_vm(self, local_file_name):
        """Replaces the remote config file with new contents.
        This function uses the scp program to copy the new config file
        """
        self.logger.debug(get_location())
        remote_file_name = local_file_name
        subprocess.call(['scp', '-q', '-i', self.key_file_path,
                         '-P', self.tcp_port,
                         '-o', 'StrictHostKeyChecking=no',
                         f'{local_file_name}',
                         f'{self.host_address}:{remote_file_name}'])
        os.remove(local_file_name)
    # -------------------------------------------------------------------------
# =============================================================================

class LeniencyLevel(IntEnum):
    """ Represents the modes of the string compariaaon tests
        The values are used and tested as bitflags.
        Values are additive only for the non-numbered enums
    """
    RegularEqual = 0
    IgnoreCase = 1
    IgnoreLineEnding = 2
    IgnoreWhitespaces = 4
    Ignore2CaseWhitespace = 5
    Ignore2CaseLineEnding = 3
    Ignore3CaseWhitespaceEnding = 7
# =============================================================================


class TestCaseSI(unittest.TestCase):
    """ Wrap-around for more lenient string comparison with the following options:
        1. Case insensitive string comparison (ignores string case)
        2. Ignores line endings ('\\n', '\\n\\r', '\\t\\n', etc)
        3. Ignores  white-spaces (re('\\s+'), etc)
    """
    def runTest(self):
        # super().runTest()
        pass

    def __init__(self, *f_args, **f_kwargs):
        """
        """
        super().__init__(*f_args, **f_kwargs)
        self.level = LeniencyLevel.Ignore3CaseWhitespaceEnding
        self.whitespaces = ['\t', '\n', '\r', '\x0b', '\x0c', '\x0f']
        self.ws_regex = re.compile(r'\s+')
        self.easy_exceptions = list()
        # self.tests = []
    # -------------------------------------------------------------------------
    def get_error_details(self, error) -> str:
        error_type, error_value, error_trace_back = sys.exc_info()
        extra = traceback.format_exception(error_type, error_value, error_trace_back)
        message = self. make_log_message(error)
        return   f'{datetime.now().astimezone().isoformat(sep=" ")}:{message}\n\t{extra}'
    # -------------------------------------------------------------------------

    def make_log_message(self, error)->str:
        """ Makes Log Message as specified
        Args:
            error (_type_): _description_
        Returns:
            str: specified error message to log
        """
        parts = {}
        if hasattr(error, '__class__'):
            parts['Type'] = getattr(error, '__class__')
        else:
            parts['Type'] = type(error)
        if hasattr(error, 'message'):
            parts['Error'] = getattr(error,  'message')
        else:
            parts['Error'] = str(error)
        return f'\n\tType: {parts["Type"]}\n\tError: {parts["Error"]}'
    # -------------------------------------------------------------------------
    
    def extend_whitespaces(self, new_whitespaces: list):
        """ Allows to add whitespaces besides the default ones (if needed)
        """
        if new_whitespaces:
            space_set = set(self.whitespaces)
            space_set |= set(new_whitespaces)
            self.whitespaces = list(space_set)
    # -------------------------------------------------------------------------

    def refresh_regex(self):
        """ Generates regex to cover whitespaces to be removed
        """
        default_regex = re.compile(r'\s+')
        # print(f'Spaces: {self.whitespaces}') # Debug
        if self.whitespaces:
            ws_regex = r'(\s' # Default whitespaces
            for space in self.whitespaces:
                to_add = re.sub(default_regex, '', space)
                if to_add: # Add only if wildcard can't takes care of it
                    ws_regex += f'|{space}'
            ws_regex += ')+'
            # print(f'RegEx = {ws_regex}') # Debug
            self.ws_regex = re.compile(ws_regex)
        return self.ws_regex
    # -------------------------------------------------------------------------

    def report_assertion(self, comp_level: LeniencyLevel,
                         assertion: AssertionError,
                         in_str1: str, in_str2: str,
                         mod_str1: str, mod_str2: str):
        """ Compose and append the assertion report statement for the assertion
        """
        self.easy_exceptions.append(f'Assertion Error Comparing @ {comp_level}:'
                                    f'\n\t[{mod_str1}]\nand\n\t[{mod_str2}]'
                                    f'\nOriginating from:'
                                    f'\n\t[{in_str1}]\nand\n\t[{in_str2}]'
                                    f'\nOriginal Error Was: [{assertion}]')
    # -------------------------------------------------------------------------

    def get_breakless_text(self, text: str) -> str:
        """ Removes linebreaks and empty strings representing multiple linebreaks
        """
        return ''.join([c for c in text.strip().splitlines() if c])
    # -------------------------------------------------------------------------

    def assertEasyEqual(self, string1, string2):
        """ Performs the main comparison functionality of the string
            comparison assertion extended by the leniency
        """
        if (not (isinstance(string1, str) and isinstance(string2, str))
                or self.level & LeniencyLevel.RegularEqual):
            super().assertEqual(string1, string2)   # Sanity shortcut to a regular assert
            return
        # 1. Perform CaSe-less string comparisson
        str1 = string1
        str2 = string2
        if self.level & LeniencyLevel.IgnoreCase:
            # Bring both string to the lower register
            str1 = str.lower(str1)
            str2 = str.lower(str2)
            try:
                self.assertEqual(str1, str2)
            except AssertionError as assertion:
                self.report_assertion(LeniencyLevel.IgnoreCase,
                                      assertion, string1, string2, str1, str2)
        # Perform Break-less string comparisson
        no_breaks1 = str1
        no_breaks2 = str2
        if self.level & LeniencyLevel.IgnoreLineEnding:
            no_breaks1 = self.get_breakless_text(no_breaks1)
            no_breaks2 = self.get_breakless_text(no_breaks2)
            try:
                self.assertEqual(no_breaks1, no_breaks2)
            except AssertionError as assertion:
                self.report_assertion(LeniencyLevel.IgnoreCase,
                                      assertion, string1, string2, no_breaks1, no_breaks2)
        # Perform Space-less string comparisson
        no_space1 = no_breaks1
        no_space2 = no_breaks2
        if self.level & LeniencyLevel.IgnoreWhitespaces:
            self.refresh_regex()
            # Split both strings by ALL-&-ANY whitespaces
            # not the most efficient way, but the most universal
            no_space1 = re.sub(self.ws_regex, '', no_space1)
            no_space2 = re.sub(self.ws_regex, '', no_space2)
            try:
                self.assertEqual(no_space1, no_space2)
            except AssertionError as assertion:
                self.report_assertion(LeniencyLevel.IgnoreCase,
                                      assertion, string1, string2, no_space1, no_space2)
    # -------------------------------------------------------------------------
# =============================================================================


class TestRunnerSI(unittest.TextTestRunner):
    """ Wrapper for test runner to force non-empty result object return
    """
    def __init__(self, *f_args, **f_kwargs):
        super(TestRunnerSI, self).__init__(*f_args, **f_kwargs)
        self.results_tci = TestResultsSI()
    # -------------------------------------------------------------------------

    def _makeResult(self):
        """ That's what was missing.
        """
        super(TestRunnerSI, self)._makeResult()
        print(f'Returning {self.results_tci}')
        return self.results_tci
    # -------------------------------------------------------------------------
# =============================================================================


class TestResultsSI(unittest.TestResult):
    """ TCI Specific test result accumulation and reporting functionality
    """
    def __init__(self, *f_args, **f_kwargs):
        self.test_results = []
        super(TestResultsSI, self).__init__(*f_args, **f_kwargs)
    # -------------------------------------------------------------------------

    def append_test_result(self, test, resultType: str = 'SUCCESS', err=None):
        """ Aggregates the record keeping for the add{Error|Failure|Success} functions
        """
        rec = {}
        name_with_class = test.__str__()
        test_name = name_with_class.split()[0]
        rec['result'] = resultType
        rec['test_name'] = test_name
        rec['doc'] = test.shortDescription()
        rec['error'] = 'OK' if (not err)  else err
        if err and resultType=='ERROR':
            print(f'\nError:\nE1:{err[0]}\nE2:{err[1]}\nE3:{err[2]}\n')            
        sys.stdout.write('.')
        sys.stdout.flush()
        self.test_results.append(rec)
        # print(f'\n\n Appended {rec}\n Results:\n{self.test_results}\n\n')
    # -------------------------------------------------------------------------

    def addError(self, test, err):
        """Save the test's name and the first line of its docstring.
        """
        # print(f'inside addError: {err}\nTest: {test.__str__().split()[0]}\n')
        super(TestResultsSI, self).addError(test, err)
        self.append_test_result(test, 'ERROR', err)
    # -------------------------------------------------------------------------

    def addFailure(self, test, err):
        """Save the test's name and the first line of its docstring.
        """
        # print(f'inside addFailure: {err}\nTest: {test.__str__().split()[0]}')
        super(TestResultsSI, self).addFailure(test, err)
        self.append_test_result(test, 'FAILURE', err)
    # -------------------------------------------------------------------------

    def addSuccess(self, test):
        """Save the test's name and the first line of its docstring.
        """
        # print(f'inside addSuccess: {test}\nTest: {test.__str__().split()[0]}')
        super(TestResultsSI, self).addSuccess(test)
        self.append_test_result(test)
    # -------------------------------------------------------------------------

    def addSkip(self, test, reason: str) -> None:
        self.append_test_result(test, 'SKIPPED', reason)
        return super().addSkip(test, reason)
    # -------------------------------------------------------------------------

    def stopTest(self, test):
        THIS_MODULE.TEST_STATUS = self
    # -------------------------------------------------------------------------
# =============================================================================


class TestStrings(TestCaseSI):  # unittest.TestCase,
    """ Punch-bag class to try out modes of using subclass in Echo Test
    """
    def __init__(self, *f_args, **f_kwargs):
        super().__init__(*f_args, **f_kwargs)
        return
    # -------------------------------------------------------------------------

    def test_2_same_strings(self):
        """ Compares same strings to test SUCCESS logging
        """
        s = 'Xx Ii Oo'
        print(get_location())
        self.assertEasyEqual(s, s)
        self.assertEqual(s, s)
    # -------------------------------------------------------------------------

    def test_2strings(self):
        """ Compares X to x repeated 1024 times
        """
        print(get_location())
        self.assertEasyEqual('Xs' * 1024 + '\n', 'x' * 1024 + '')
        self.assertNotEqual('Xs' * 1024 + '\n', 'x' * 1024 + '')
    # -------------------------------------------------------------------------

    def test_one_word(self):
        """ Compares Hello to hello
        """
        print(get_location())
        self.assertEasyEqual('hello\n', "Hello")
        self.assertNotEqual('hello\n', "Hello")
    # -------------------------------------------------------------------------

    def test_2nums(self):
        """ Compares 123 to 456 and MUST FAIL
        """
        print(get_location())
        self.assertEasyEqual(123, 456)
        self.assertEqual(123, 456)
    # -------------------------------------------------------------------------
# =============================================================================


if __name__ == "__main__":  # The test harness for trying out the extensions of the test-suite

    print(f'\n{"*"*120}\n')
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestStrings)
    runner = unittest.TextTestRunner(resultclass=TestResultsSI, failfast=False, verbosity=2) # (verbosity=0|1)
    result = runner.run(suite)
    res = TestResultsSI(result)

    res = THIS_MODULE.TEST_STATUS
    # print(f'\n\nType = {type(res)}\n')
    # print(f'{dir(res)}')
    # print(f'Length: {len(res.test_results)}\n Array: {res.test_results}')
    # print(f'Errors: {res.errors}')
    # print(f'Failures: {res.failures}')
    # print(f'Eroors: {res.errors}')
    num_successes = len([x for x in res.test_results if x['result'] == 'SUCCESS'])
    num_failures = len([x for x in res.test_results if x['result'] == 'FAILURE'])
    num_errors = len([x for x in res.test_results if x['result'] == 'ERROR'])
    num_tests = num_successes + num_failures + num_errors
    out_line = (f'{num_tests} tests: {num_successes} '
                f'successes, {num_failures} failures, {num_errors} errors')
    print(out_line)
    for test_rec in res.test_results:
        print(test_rec['result'] + ': ' + test_rec['test_name'])
        print('         ' + test_rec['doc'])
