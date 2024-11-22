#!/usr/bin/env python3
"""Unit tests for the Homework programs.

This program requires SSH to be set up!


1) copy this program to /root on the VM
2) copy the Homework program to /root on the VM
3) make sure that both programs are executable (chmod +x if necessary).
4) copy the vm.key file to /root on the VM
5) as root, and in the /root directory, type: ./test_homework.py

Note: vmconf.py generates the auto_vm.key file when it creates a vm.

Note a few idioms in this code: local variables that must exist (e.g.,
three elements of a tuple are returned from a function but only one is
used) but are unused, are prefixed by '_'; this suppresses some
warnings from the pylint code scanner.
"""
__author__ = "Dmitry Cousin"
__status__ = "Prototype"
import os
import subprocess
import sys
import unittest
import si_server_utils as utils
import si_server_test_utils as test_utils


IS_DEBUGGING = False
def print_if(line:str):
    if IS_DEBUGGING:
        print(line)        
#---------------------------------------------------------------------------------------------

class VMHomeResolver:
    
    VM_HOME = None

    def __init__(self, host_address: str, tcp_port: str, key_file_path: str,):
        self.host_address = host_address
        self.tcp_port = tcp_port
        self.key_file_path = key_file_path

    def get_home_on_vm(self, ):
        """ Retrieve home directory from the VM 
        """
        if not VMHomeResolver.VM_HOME:
            print_if(test_utils.get_location())
            ssh_pwd = [ 'ssh', self.host_address,
                        '-p', self.tcp_port,
                        '-i', self.key_file_path,
                        '-o', 'StrictHostKeyChecking=no', '-q',
                        'pwd']
            try:
                stdout, stderr  = subprocess.Popen(ssh_pwd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT
                                        ).communicate()
                VMHomeResolver.VM_HOME = stdout.decode('utf-8').strip()
            except subprocess.CalledProcessError:
                print_if('subprocess.Popen of ssh returned error!')
            finally:
                return VMHomeResolver.VM_HOME
        else:
            return VMHomeResolver.VM_HOME
    # -------------------------------------------------------------------------
    def resolve_hw_vm_home(self, path:str) :
        return path.replace('~/', f"{self.get_home_on_vm()}/")
#---------------------------------------------------------------------------------------------


class TestContext:
    INPUT_ARGS = None
    TESTED_SERVER = None
    LOGGER = None
    LOG_NAME = None
    HOMEWORK = 3
    APP_TO_TEST = 'python3 hw3.py'
    KEY_FILE_PATH = ''
    SSH_TARGET = None
    SERVER_TO_TEST = None
    SKIP_SLOW_TESTS = False
    CONTEXT = 1
    TCP_PORT = None
    USER_OF_SERVER = ''
    JSON_FILE = ''
    APP_DEFAULT = utils.AppToExecute.NOOP
    

    @classmethod
    def init_context(cls, setup_args: utils.VmTestArguments):
        cls.INPUT_ARGS = setup_args.app_args
        cls.HOMEWORK = setup_args.homework_number
        cls.LOG_NAME = setup_args.logger_file_name
        cls.LOGGER = setup_args.logger
        cls.SSH_TARGET = setup_args.user_at_address
        cls.KEY_FILE_PATH = setup_args.key_file_path
        cls.SKIP_SLOW_TESTS = not setup_args.deep_test_level <= 0
        cls.TCP_PORT = setup_args.tcp_port
        cls.APP_TO_TEST = setup_args.app_to_run
        cls.USER_OF_SERVER = setup_args.user_at_address
        cls.JSON_FILE = setup_args.json_file_name
        cls.APP_DEFAULT = setup_args.app_defaults
        cls.ADDRESS =  setup_args.ssh_address

        cls.HomeResolver = VMHomeResolver(cls.USER_OF_SERVER, cls.TCP_PORT, cls.KEY_FILE_PATH)
        # TODO: For now ignore Database-Based Scoring, maybe will re-add it later
        # ------------------------------------------------------------------------    
        # score_init.prepare_scoring_information(input_args=THIS_MODULE.INPUT_ARGS,
        #                                         test_file=os.path.join(os.getcwd(), __file__),
        #                                         test_type=ScoreSuffix.EVENT)
        if ((not cls.KEY_FILE_PATH)
                or (not os.path.isfile(cls.KEY_FILE_PATH))):
            cls.LOGGER.critical(f'Error: SSH key file\n\t[{cls.KEY_FILE_PATH}]\n'
                                        f'does not exist')
            sys.exit()
        else:
            cls.LOGGER.debug(f'SSH key resolved to: [{cls.KEY_FILE_PATH}]')
        
    @classmethod
    def get_test_type(cls)->type:
        if cls.HOMEWORK == 1:
            return TestHomeworkOne
        elif cls.HOMEWORK == 2:
            return TestHomeworkTwo
        elif cls.HOMEWORK == 3:
            return TestHomeworkThree
        elif cls.HOMEWORK == 4:
            return TestHomeworkFour
        # elif cls.HOMEWORK == 5:
        #     return TestHomeworkFive
        # elif cls.HOMEWORK == 6:
        #     return TestHomeworkSix
        
    #-----------------------------------------------------------------------------------------
#=============================================================================================



class HWSettings:

    MSG_EXIT_BAD_CONFIG = 'Corrupt config file!\n'
    MSG_EXIT_BYE = 'Bye!\n'

    MSG_ACC_APP_LIMIT = 'Account logins limit exceeded!'
    MSG_ACC_LOCKED = 'Account locked or either user name, password, or both are incorrect!'
    MSG_BAD_LOGIN = 'Either user name, password, or both are incorrect!'

    MSG_UI_USER_NAME = 'User Name:'
    MSG_UI_PASSWORD = 'Password:'

    MAIN_MENU_HW1 = ('0.[E]xit 1.[U]ser 2.[T]able:')
    MAIN_MENU_HW2 = ('0.[E]xit 1.[S]ettings:')
    MAIN_MENU_HW3 = ('0.[E]xit 1.[S]ettings 2.[D]ata:')
    MAIN_MENU_HW4 = ('0. [E]xit 1. [S]ettings 2. [L]ogin:')
    MAIN_MENU_HW5 = ('0. [E]xit 1. [S]ettings 2. [L]ogin:')

    MAIN_MENU_ACT_Exit = ['0', 'E', 'Exit']
    MAIN_MENU_ACT_Settings = ['1', 'S', 'Settings']
    MAIN_MENU_ACT_Login = ['2', 'L', 'Login'] 
    MAIN_MENU_ACT_Data_HW3 = ['2', 'D', 'Data'] 
    MAIN_MENU_ACT_User_HW1 = ['2', 'U', 'User'] 
    MAIN_MENU_ACT_Table_HW1 = ['3', 'T', 'Table'] 

    DEFAULT_CONFIG={
        'DB_FILE': '~/si/db/SI_DB.db', 
        'LOG_FILE': '~/si/logs/SI_Log.txt', 
        'TABLE_NAME': 'Users_Top50', 
        'MAX_FAILED': 6,
    }

    KEYS_PROFILE = ['User-Id:', 'User-Name:', 'Failed-Count', 'Entries-Count' ]

    DEFAULT_CONFIG_STRING =[
            "DB_FILE: ~/si/db/SI_DB.db",
            "LOG_FILE: ~/si/logs/SI_Log.txt",
            "MAX_FAILED: 6",
            "TABLE_NAME: Users_Top50"]
    
    HASHED_CONFIG_STRING =[
            "DB_FILE: ~/si/db/SI-HW4.db",
            "LOG_FILE: ~/si/logs/SI_Log_HW4.txt",
            "MAX_FAILED: 6",
            "TABLE_NAME: Users_Top50H"]
    
    DUMMY11_CLEAN=[
        'User-Id: 11', 
        'User: dummy11', 
        'Failed-Count: 0', 
        'Entries-Count: 1',         
    ]

    DUMMY11_FAILED_2=[
        'User-Id: 11', 
        'User: dummy11', 
        'Failed-Count: 2', 
        'Entries-Count: 1',         
    ]


    @classmethod
    def get_config_string(cls, hw_number: int) -> str:
        if hw_number <= 3 :
            return cls.DEFAULT_CONFIG_STRING
        elif hw_number == 4 :
            return cls.HASHED_CONFIG_STRING
        
    @classmethod
    def shape_output(cls, set_lines: list, menu:str) -> str:
        result = '\n'
        lines_copy = set_lines[:]
        lines_copy.append(menu)
        print_if(f'\n\tSet: {lines_copy}, \n\tType: {type(lines_copy)}')
        result = '\n'.join(lines_copy)
        return result
    #-----------------------------------------------------------------------------------------
#=============================================================================================



class TestHomeworkBase(test_utils.TestCaseSI):
    """Test Suite for a program satisfying the homeworks.md specification."""
    #pylint: disable=too-many-public-methods
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        """After all the testing is done, remove any "testing" conf file."""
        # THIS_MODULE.SERVER_TO_TEST.kill_remote_file('conf')
        pass

    @classmethod
    def dump_info_out(cls, file_name, text):
        """ The class method to write down a file
        """
        TestContext.LOGGER.debug(f'Writing information out to file: {file_name}')
        with open(file_name, "w+") as f:
            f.write(text)
            
    def print_couple(self, target, response, relation: str='', extra:str = '' ):
        if extra:
            print(f"\n{'='*80}\nBEGIN @Iteration# {extra}:")
        else:
            print(f"\n{'='*80}\nBEGIN")
        print("\n\tTarget:")
        print(target)
        if relation: 
            print(f"\t{relation}Response:")
        else:
            print(f"\n\tResponse:")
        print(response)
        print(f"\nEND\n{'='*80}\n:")

    def get_vm_config(self, conf_list:list):
        print_if(conf_list)
        resolved = [TestContext.HomeResolver.resolve_hw_vm_home(chunk) if '_FILE: ' in chunk else chunk
                    for chunk in conf_list]
        print_if(conf_list)
        return resolved

    def tearDown(self):
        """ Tear-down per test method
        """
        # print("Instance-Method: tearDown\n")
        pass

    def setUp(self):
        """ Create clean datastore, config, and start the Homework.
        """
        # pylint: disable=invalid-name
        TestContext.LOGGER.debug(f'{"!"*68}\nAbout to run {self.id}\n{"!"*68}')
        self.maxDiff = None  #Allow long messages from assert() methods.
        # THIS_MODULE.SERVER_TO_TEST.push_remote_file('conf', DEFAULT_CONFIG)
        self.hw_number = TestContext.HOMEWORK

        try:
            pass
            # TestContext.SERVER_TO_TEST.reset_server('conf')
        except Exception as ex:
            self.fail(ex)
    #--------------------------------------------------------------------------------------------------------------

    def get_context_menu(self):
        if TestContext.HOMEWORK==1:
            CURRENT_MENU = HWSettings.MAIN_MENU_HW1
        elif TestContext.HOMEWORK==2:
            CURRENT_MENU = HWSettings.MAIN_MENU_HW2
        elif TestContext.HOMEWORK==3:
            CURRENT_MENU = HWSettings.MAIN_MENU_HW3
        elif TestContext.HOMEWORK==4:
            CURRENT_MENU = HWSettings.MAIN_MENU_HW4
        return CURRENT_MENU
    #--------------------------------------------------------------------------------------------------------------

#==================================================================================================================

class TestHomeworkOne(TestHomeworkBase):
    @classmethod
    def setUpClass(cls):
        pass
    # @unittest.parameterized.expand([ tuple(['']),tuple(['open sesame']),tuple(['git']),
    #     tuple(['exit only']), tuple(['logins']), tuple(['setting and other stuff'])]) 
    @unittest.skipIf(TestContext.HOMEWORK < 1, 'No Menus for Homeworks Less Than 3')
    def test_func_main_menu_wrong(self):
        """ Verifies that the message [Input 'Value of the Input' is unknown!] is shown for the incorrect inputs
        """
        CURRENT_MENU = self.get_context_menu()
        print_if('\n!!!\tEntering test_func_main_menu')
        TestContext.LOGGER.debug('test_func_main_menu')
        wrong_commands = ['', 'open sesame', 'git', 'exit only', 'logins', 'setting and other stuff']
        proc = None
        try:
            proc, response = TestContext.SERVER_TO_TEST.start_server_ext(expected_response_endswith=CURRENT_MENU)
            self.assertEqual(CURRENT_MENU, response)
            for surprise_string in wrong_commands:
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, surprise_string , response_end=CURRENT_MENU)
                self.assertEqual(f"Input '{surprise_string}' is unknown!\n{CURRENT_MENU}", response)
        except AssertionError as ae:
            TestContext.LOGGER.exception(ae, exc_info=True)
            self.fail( self.get_error_details(ae))
        except Exception as ex:
            TestContext.LOGGER.exception(ex, exc_info=True)
            self.fail(self.get_error_details(ex))
        finally:
            print_if('Finally!')
            if proc:
                TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------

    @unittest.skipIf(TestContext.HOMEWORK<1, 'No Menus for Homeworks Less Than 3') 
    def test_func_main_menu(self):
        """ Makes sure that the main menu for the app shows up 
        """
        CURRENT_MENU = self.get_context_menu()
        print_if('\n!!!\tEntering test_func_main_menu')
        TestContext.LOGGER.debug('test_func_exit_command')
        proc = None
        try:
            proc, response = TestContext.SERVER_TO_TEST.start_server_ext(expected_response_endswith=CURRENT_MENU)
            print_if(f'Pre-Menu3 test_func_quit_command\n\t {response}')
            self.assertEqual(CURRENT_MENU, response)
            response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, '0' , response_end=HWSettings.MSG_EXIT_BYE)
        except AssertionError as ae:
            TestContext.LOGGER.exception(ae, exc_info=True)
            self.fail( self.get_error_details(ae))
        except Exception as ex:
            TestContext.LOGGER.exception(ex, exc_info=True)
            self.fail(self.get_error_details(ex))
        finally:
            print_if('Finally!')
            if proc:
                TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------

    @unittest.skipIf(TestContext.HOMEWORK<1, 'No Menus for Homeworks Less Than 3')
    def test_func_exit_options_array(self):
        """Homework must exit if either option ['0', 'e', 'E', 'Exit', 'ExIt', 'EXIT', 'exit']
          is entered for Main Menu right after start
        """
        CURRENT_MENU = self.get_context_menu()
        print_if('\n!!!\tEntering test_func_exit_options')
        TestContext.LOGGER.debug('test_func_exit_command')
        proc = None
        for inputX in ['0', 'e', 'E', 'Exit', 'ExIt', 'EXIT', 'exit']:
            try:
                proc, response = TestContext.SERVER_TO_TEST.start_server_ext(expected_response_endswith=CURRENT_MENU)
                print_if(f'Pre-Menu3 test_func_quit_command\n\t {response}')
                self.assertEqual(CURRENT_MENU, response)
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, inputX , response_end=HWSettings.MSG_EXIT_BYE)
                self.assertEqual('Bye!\n', response)
                TestContext.SERVER_TO_TEST.stop_server(proc)
                print_if(f'Post Bye! test_func_quit_command\n{response}\tAfter TYPING: "{inputX}"\n\n')
            except AssertionError as ae:
                details = self.get_error_details(ae)
                print_if(f'{details}\n{ae}')
                TestContext.LOGGER.exception(f'{details}\n{ae}', exc_info=True)
                self.fail(details)
            except Exception as ex:
                details = self.get_error_details(ex)
                print_if(f'{details}\n{ex}')
                TestContext.LOGGER.exception(f'{details}\n{ex}', exc_info=True)
                self.fail(details)
            finally:
                print_if('Finally!')
                if proc:
                    TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------

    # TODO: Add Good User-Input => No Logs verification test
    # TODO: Add Bad User-Input => Logs verification test
    # TODO: Add Log-Existence verification test
    # TODO: Add Log-Content verification test

#==================================================================================================================


class TestHomeworkTwo(TestHomeworkOne):
    @classmethod
    def setUpClass(cls):
        pass
    #--------------------------------------------------------------------------------------------------------------

 
    @unittest.skipIf(TestContext.HOMEWORK<2, 'No Config reading for Homeworks Less Than 2') 
    def test_func_bad_config(self):
        """ Makes sure that invalid YAML settings file stops the application
        """
        print_if('\n!!!\tEntering test_func_main_menu')
        TestContext.LOGGER.debug('test_func_exit_command')
        proc = None
        try:
            proc, response = TestContext.SERVER_TO_TEST.start_server_ext(conf = ' -config ~/si/set/settings-broken.yaml', expected_response_endswith=HWSettings.MSG_EXIT_BAD_CONFIG)
            self.assertEqual(HWSettings.MSG_EXIT_BAD_CONFIG, response)
        except AssertionError as ae:
            TestContext.LOGGER.exception(ae, exc_info=True)
            self.fail( self.get_error_details(ae))
        except Exception as ex:
            TestContext.LOGGER.exception(ex, exc_info=True)
            self.fail(self.get_error_details(ex))
        finally:
            print_if('Finally!')
            if proc:
                TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------
    # TODO: Add Broken User-Name => Log-Content test
    # TODO: Add Broken Table-Name => Log-Content test
#==================================================================================================================

class TestHomeworkThree(TestHomeworkTwo):

    #--------------------------------------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------------------------------------

    @unittest.skipIf(TestContext.HOMEWORK<3, 'No Menus for Homeworks Less Than 3')
    def test_func_settings_data_once(self):
        """Homework must match reproduced and ~/ resolved to /home/<user-name> sorted default settings multiline text
        """
        CURRENT_MENU = self.get_context_menu()
        print_if('\n!!!\tEntering test_func_settings_data')
        TestContext.LOGGER.debug('test_func_exit_command')
        # set_str = HW_Settings.DEFAULT_CONFIG_STRING[:]
        # set_str.append(CURRENT_MENU)
        # print_if(f'\n\tSet: {set_str}, \n\tType: {type(set_str)}')
        # MATCH_SETTINGS =  '\n'.join(set_str)
        list_conf = list( HWSettings.get_config_string(TestContext.HOMEWORK) )
        vm_config = self.get_vm_config(list_conf)
        MATCH_SETTINGS =  HWSettings.shape_output(vm_config, CURRENT_MENU) # 
        proc = None
        try:
            proc, response = TestContext.SERVER_TO_TEST.start_server_ext(expected_response_endswith=CURRENT_MENU)
            self.assertEqual(CURRENT_MENU, response)
            response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, 'Settings' , response_end=CURRENT_MENU)

            print_if(f'\nResponse:\n{response}')
            print_if(f'\nDefault:\n{MATCH_SETTINGS}')

            self.assertEqual(MATCH_SETTINGS, response)
            print_if(f'test_func_settings_data:\n\t{response}')
            # set_dict = {}
            # for line in response:
            #     (k, v) = line.split(':')
            #     set_dict[k] = v
            # print_if(set_dict)

        except AssertionError as ae:
            details = self.get_error_details(ae)
            print_if(f'{details}\n{ae}')
            TestContext.LOGGER.error(f'{details}\n{ae}', exc_info=True)
            self.fail(details)
        except Exception as ex:
            details = self.get_error_details(ex)
            print_if(f'{details}\n{ex}')
            TestContext.LOGGER.exception(f'{details}\n{ex}', exc_info=True)
            self.fail(details)
        finally:
            print_if('Finally!')
            if proc:
                TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------

    @unittest.skipIf(TestContext.HOMEWORK<3 , 'No Menus for Homeworks Less Than 3')
    def test_func_settings_data_options_array(self):
        """ Array of possibilities for choosing settings ['1', 's', 'S', 'Settings', 'SeTtinGS', 'SETTINGS', 'settings']
            Homework must match reproduced and ~/ resolved to /home/<user-name> sorted default settings multiline text
        """
        print_if('\n!!!\tEntering test_func_settings_data')
        TestContext.LOGGER.debug('test_func_exit_command')

        CURRENT_MENU = self.get_context_menu()
        str_conf = list( HWSettings.get_config_string(TestContext.HOMEWORK) )
        vm_config = self.get_vm_config(str_conf)
        MATCH_SETTINGS =  HWSettings.shape_output(vm_config, CURRENT_MENU) # 
        proc = None
        for inputX in ['1', 's', 'S', 'Settings', 'SeTtinGS', 'SETTINGS', 'settings']:
            try:
                proc, response = TestContext.SERVER_TO_TEST.start_server_ext(expected_response_endswith=CURRENT_MENU)
                self.assertEqual(CURRENT_MENU, response)
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, inputX , response_end=CURRENT_MENU)

                print_if(f'\nResponse:\n{response}')
                print_if(f'\nDefault:\n{MATCH_SETTINGS}')

                self.assertEqual(MATCH_SETTINGS, response)
                print_if(f'test_func_settings_data:\n\t{response}')

            except AssertionError as ae:
                details = self.get_error_details(ae)
                print_if(f'{details}\n{ae}')
                TestContext.LOGGER.error(f'{details}\n{ae}', exc_info=True)
                self.fail(details)
            except Exception as ex:
                details = self.get_error_details(ex)
                print_if(f'{details}\n{ex}')
                TestContext.LOGGER.exception(f'{details}\n{ex}', exc_info=True)
                self.fail(details)
            finally:
                print_if('Finally!')
                if proc:
                    TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------
#==================================================================================================================


class TestHomeworkFour(TestHomeworkThree):
    #--------------------------------------------------------------------------------------------------------------

    # @unittest.skipIf(TestContext.HOMEWORK<4 , 'No DB Homeworks Less Than 4')
    def test_func_login_clean_profile_array(self):
        """ Array of possibilities for choosing Login Option ['2', 'l', 'L', 'Login', 'LoGiN', 'LOGIN', 'login']
            Homework must match clean profile of the user dummy11
        """
        response = ''
        CURRENT_MENU = self.get_context_menu()
        print_if('\n!!!\tEntering test_func_settings_data')
        TestContext.LOGGER.debug('test_func_exit_command')
        MATCH_PROFILE_11 =  HWSettings.shape_output(HWSettings.DUMMY11_CLEAN, CURRENT_MENU) # 
        proc = None
        for idx, inputX in enumerate(['2', 'l', 'L', 'Login', 'LoGiN', 'LOGIN', 'login']):
            try:
                proc, response = TestContext.SERVER_TO_TEST.start_server_ext(expected_response_endswith=CURRENT_MENU)
                self.assertEqual(CURRENT_MENU, response)
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, inputX , response_end='User Name:')

                # User Name:
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, 'dummy11' , response_end='Password:')
                # Password:
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, '123123' , response_end=CURRENT_MENU)

                print_if(f'\nResponse:\n{response}')
                print_if(f'\nDefault:\n{MATCH_PROFILE_11}')

                # self.assertEqual('\n'+MATCH_PROFILE_11, response)
                if idx>0: # Skip the first login to make sure that the logins are reset to 0 by a successful login at 0
                    self.assertEqual(MATCH_PROFILE_11.strip(), response.strip())                

                print_if(f'test_func_settings_data:\n\t{response}')

            except AssertionError as ae:
                print(f"\n\tResponse:\n{response}\n\n\tExpected:\n{MATCH_PROFILE_11}")
                details = self.get_error_details(ae)
                print_if(f'{details}\n{ae}')
                TestContext.LOGGER.error(f'{details}\n{ae}', exc_info=True)
                self.fail(details)
            except Exception as ex:
                print(f"\n\tResponse:\n{response}\n\n\tExpected:\n{MATCH_PROFILE_11}")
                details = self.get_error_details(ex)
                print_if(f'{details}\n{ex}')
                TestContext.LOGGER.exception(f'{details}\n{ex}', exc_info=True)
                self.fail(details)
            finally:
                print_if('Finally!')
                if proc:
                    TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------

    # @unittest.skipIf(TestContext.HOMEWORK < 4, 'No DB Homeworks Less Than 4')
    def test_func_login_nonzero_failed_counts(self):
        """ Array of possibilities for choosing Login Option ['2', 'l', 'L', 'Login', 'LoGiN', 'LOGIN', 'login']
            Homework must match clean profile of the user dummy11
        """
        target_match = ''
        response = ''
        CURRENT_MENU = self.get_context_menu()
        print_if('\n!!!\tEntering test_func_settings_data')
        TestContext.LOGGER.debug('test_func_exit_command')
        MATCH_PRO_11 =  HWSettings.shape_output(HWSettings.DUMMY11_CLEAN, CURRENT_MENU) # 
        MATCH_PRO_1F2 =  HWSettings.shape_output(HWSettings.DUMMY11_FAILED_2, CURRENT_MENU) # 
        passwords = ['123123','', '', '123123', '', '', '123123', '123123']
        proc = None
        for idx, inputX in enumerate(['2', 'l', 'L', 'Login', 'LoGiN', 'LOGIN', 'login', 'login']):
            try:
                proc, response = TestContext.SERVER_TO_TEST.start_server_ext(expected_response_endswith=CURRENT_MENU)
                self.assertEqual(CURRENT_MENU, response)
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, inputX , response_end='User Name:')

                # User Name:
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, 'dummy11' , response_end='Password:')
                # Password:
                response = TestContext.SERVER_TO_TEST.type_to_server_ext(proc, passwords[idx] , response_end=CURRENT_MENU)

                print_if(f'\nResponse:\n{response}')
                print_if(f'\nDefault:\n{MATCH_PRO_11}')

                if passwords[idx]=='' or idx in [0, 1, 2, 4, 5]: # Skip the first as failed count may still be not zero
                    # self.print_couple(MATCH_PRO_1F2.strip(), response.strip(), '!=', extra = f"{idx}")
                    target_match = MATCH_PRO_1F2.strip()
                    self.assertNotEqual(target_match, response.strip())
                if idx in [3, 6] :
                    # self.print_couple(MATCH_PRO_1F2.strip(), response.strip() , '==', extra = f"{idx}")
                    target_match = MATCH_PRO_1F2.strip()
                    self.assertEqual(target_match, response.strip())
                if idx == 7:
                    # self.print_couple(MATCH_PRO_11.strip(), response.strip(), '==', extra = f"{idx}")
                    target_match = MATCH_PRO_11.strip()
                    self.assertEqual(target_match, response.strip())

                print_if(f'test_func_settings_data:\n\t{response}')

            except AssertionError as ae:
                if idx in [0, 1, 2, 4, 5]:
                    self.print_couple(target_match, response.strip(), '!=/<>', extra = f"{idx}")
                else:
                    self.print_couple(target_match, response.strip(), '==/=', extra = f"{idx}")

                details = self.get_error_details(ae)
                print_if(f'{details}\n{ae}')
                TestContext.LOGGER.error(f'{details}\n{ae}', exc_info=True)
                self.fail(details)
            except Exception as ex:
                if idx in [0, 1, 2, 4, 5]:
                    self.print_couple(target_match, response.strip(), '!=/<>', extra = f"{idx}")
                else:
                    self.print_couple(target_match, response.strip(), '==/=', extra = f"{idx}")
                    
                details = self.get_error_details(ex)
                print_if(f'{details}\n{ex}')
                TestContext.LOGGER.exception(f'{details}\n{ex}', exc_info=True)
                self.fail(details)
            finally:
                print_if('Finally!')
                if proc:
                    TestContext.SERVER_TO_TEST.stop_server(proc)
    #--------------------------------------------------------------------------------------------------------------
#==================================================================================================================