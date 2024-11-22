#!/usr/bin/env python3
""" The separate module for scoring DB init and to avoid circular referencing
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

import argparse
# from tci.vmconf import main
from si_server_utils import VmTestArguments
from score_utils import ScoreSuffix
from score_test_vm import VmStateDbReporter
from score_test_suite import TestSuiteDbReporter


def prepare_scoring_information(input_args: VmTestArguments,
                                test_file: str,
                                test_type: ScoreSuffix = ScoreSuffix.PRACTICE):
    """ Populates scoring entries into the scoring DB
    Args:
        in_args (utils.VmTestArguments): The original Unit-Test arguments object 
        test_type (ScoreSuffix, optional): The test-Type suffix - Practice/Test/Event. 
        Defaults to ScoreSuffix.PRACTICE.
    """
    db_file = input_args.score_db_file_name
    db_dir = input_args.score_db_dir_name
    # 1. Report This-Very-Suite's Parsing-Complexity results to DB
    maker = TestSuiteDbReporter(
        test_file=test_file, test_suffix=ScoreSuffix.PRACTICE)
    # 2. Create VM-config score-reported DB object
    vmr = VmStateDbReporter(test_suffix=ScoreSuffix.PRACTICE)
    # 2-a. Report VM Configuration to the DB
    vm_name = input_args.score_vm_name
    vmr.parse_out_vm_settings(vm_name)


def parse_main_arguments():
    """[summary] Parses parameters for the initial run of the VM Setup
    """
    parser = argparse.ArgumentParser(description='TCI Score Db Init')
    parser.add_argument('-dd', metavar='db_dir', dest='db_dir', type=str,
                        help='database directory for the scoring db',
                        default='/home/tciadmin/tci-scores/')
    parser.add_argument('-db', metavar='db_name', dest='db_name', type=str,
                        help='file-name for scoring info database',
                        default='tci-scores.dbf')
    parser.add_argument('-pf', metavar='teams_file', dest='teams_file', type=str,
                        help='file-name of participants JSON information',
                        default='./toolchain/config/participants.conf'
                        )
    parser.add_argument('-vt', metavar='vm_type', dest='vm_type', type=str,
                        help='type of VM [mac-virtual, practice, event]',
                        default='mac-virtual'
                        )
    args = parser.parse_args()
    print(f'\n\tDb-Dir := {args.db_dir}')
    print(f'\n\tDb-Name := {args.db_name}')
    print(f'\n\tPart-File := {args.teams_file}')
    print(f'\n\tVM-Type := {args.vm_type}')

# ============================================================================||


if __name__ == "__main__":
    print('Running Score_Init.py')
    parse_main_arguments()
    print('Done! Running Score_Init.py')
