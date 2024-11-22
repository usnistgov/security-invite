#!/usr/bin/env python3

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

"""Unit tests for the Homework programs.

This program requires SSH to be set up!

Run it on a generated tcsubmit or vmsubmit server using the following steps:

1) copy this program to /root on the VM
2) copy the Homework program to /root on the VM
3) make sure that both programs are executable (chmod +x if necessary).
4) copy the ~/auto_vm.key file to /root on the VM
5) as root, and in the /root directory, type: ./test_homework.py

Note: vmconf.py generates the auto_vm.key file when it creates a vm.

Note a few idioms in this code: local variables that must exist (e.g.,
three elements of a tuple are returned from a function but only one is
used) but are unused, are prefixed by '_'; this suppresses some
warnings from the pylint code scanner.
"""
import datetime
import json
import logging
import os
import random
import re
import select
import string
import subprocess
import sys
import time
import unittest
import si_server_utils as utils
import si_server_test_utils as test_utils

from test_suites import TestContext, HWSettings, TestHomeworkBase
import test_suites as test_suites
__author__ = "Lee Badger, Dmitry Cousin"


# import score_init
# from score_utils import ScoreSuffix
IS_DEBUGGING = False
def print_if(line:str):
    if IS_DEBUGGING:
        print(line)
# Possibly meant for removal



# The following comment disables pylint complaints about constants
# implicitly defined at file scope (here).
# pylint: disable=invalid-name

#=============================================================================================

Homework3 ={
    "Homework_Number": 3,
    "Has_Settings": True,
    "Has_Login": False,
}

Homework4 ={
    "Homework_Number": 4,
    "Has_Settings": True,
    "Has_Login": True,
}

HW_Settings = HWSettings()
TEST_CONTEXT=Homework3


def main():
    """Parse command line parameters and invoke unit test suite.

    The output may be printed or saved to a JSON file that looks like:
        [{"result"'   : "FAILURE",
          "test_name" : "test_func_login",
          "doc" : "this function tests the login process"},
         {"result"'   : "SUCCESS",
          "test_name" : "other_test_func_login",
          "doc" : "this function tests another login function"},
          ...]
    """
    # Create a tested Server for SI
    TestContext.init_context( utils.VmTestArguments() )

    run_report_tests(TestContext.get_test_type())


    # Local to this file DEMO testing
    # if 'hw3' in TestContext.INPUT_ARGS.app_to_run:
    #     run_report_tests(Homework3)

    # if 'hw4' in TestContext.INPUT_ARGS.app_to_run:
    #     run_report_tests(Homework4)
#------------------------------------------------------------------------------------------------------------------

def run_report_tests(test_suite_to_use: TestHomeworkBase):

    TestContext.SERVER_TO_TEST = test_utils.ServerSI(
                               app_to_test=TestContext.APP_TO_TEST,
                               host_address=TestContext.USER_OF_SERVER,
                               tcp_port=str(TestContext.TCP_PORT), # blows up if not a STRING
                               key_file=TestContext.KEY_FILE_PATH,
                               logger=TestContext.LOGGER)
    
    TestContext.SERVER_TO_TEST.verify_recreate_test_tree()
    
    TestContext.LOGGER.debug("Beginning loading tests.")

    suite = unittest.TestLoader().loadTestsFromTestCase(test_suite_to_use)
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestHomework)
    TestContext.LOGGER.debug("Creating tests runner.")
    
    
    # Normal TestRunner
    # runner = unittest.TextTestRunner(resultclass=test_utils.TestResultsSI) # resultclass=HomeworkTestResult
    # Verbose TestRunner
    runner = unittest.TextTestRunner(verbosity=2, resultclass=test_utils.TestResultsSI) # resultclass=HomeworkTestResult

    print(f'#{"="*80}')
    TestContext.LOGGER.critical(f'Beginning running of the test suite in context Homework #{TestContext.HOMEWORK}.')

    print_if(f"VM's Home-Dir is : '{TestContext.SERVER_TO_TEST.get_home_on_vm()}'")
    # Here the whole Testing Work Happens!!!
    res = runner.run(suite)

    TestContext.LOGGER.debug('After running test suite.')

    TestContext.SERVER_TO_TEST.report_test_results(test_utils.get_test_status())


    # TODO: Implement JSON and SQLite output of the test results
    if res.test_results:
        #print(json.dumps(res.test_results, indent=1))
        json_status = utils.saved_json_test_report_ok(TestContext.JSON_FILE, res)
        if json_status:
            TestContext.LOGGER.debug(f'Failed to save JSON-results: {json_status}')
    else:
        print('No Results')
#------------------------------------------------------------------------------------------------------------------
    





if __name__ == '__main__':
    main()