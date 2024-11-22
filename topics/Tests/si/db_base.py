#!/usr/bin/env python3
""" The module aggregates sql and json scoring providing functions and classes for
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
from enum import Enum
import sqlite3 as sql
import os
from pathlib import Path
import sys
import traceback
# ============================================================================||


PRINT_THRESHOLD_LEVEL = -2

def get_location(level: int = 1) -> str:
    """ Gets location description for the call place to log exact function name, file, and line
    """
    locator = sys._getframe(1) # elevate in stack to the previous position (the caller)
    return (f' func: {locator.f_code.co_name}'
            f' at line: {locator.f_lineno}'
            f' of file: {locator.f_code.co_filename} ')

def print_if(str_to_print: str, message_level=0):
    """Conditional prompt function for debugging

    Args:
        str_to_print (str): The printed message
        message_level (int, optional): The debugging-verbosity level. Defaults to 0.
    """
    if (message_level >= PRINT_THRESHOLD_LEVEL):
        print(str_to_print)


class ScoreSuffix(Enum):
    """ Enum for test-event tupe description
    """

    TEST = 0
    PRACTICE = 1
    EVENT = 2

    def get_int_value(self) -> int:
        """ Returns int value of the enum
        Returns:
        int: Returns enum value as int
        """
        return self.value

    def get_str_name(self) -> str:
        """ Returns mnemonic name
        Returns: 
            str: The name of the enum
        """
        # self is the member here
        return f'{self.name}'

    def get_suffix(self) -> str:
        """ Retuns unified suffix (can be used in table or file names)
        Returns:
            str: String of the unified suffix
        """
        # self is the member here
        # Makes the same-shape suffixes
        name = self.name.lower().capitalize()
        return f'{name}'



class BaseDB():
    """ Base class for SQLite database manipulation
    """
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
    #----------------------------------------------------------------------------
    # Suffix usually is 'Test', 'Practice', 'Event'
    # db_suffixes = [f'-{name.lower().capitalize()}' for name, member in ScoreSuffix.__members__.items()]

    def __init__(self, work_dir: str = '', db_file: str = '', 
                 must_create_db: bool = True):
        """ Default constructor for SQLite wrapper
        """
        print(f'1. @Base WDir={work_dir}\t DBF={db_file}')
        the_db_name = (db_file if db_file 
                       else f'SI-Data.db')
        the_work_dir = (work_dir if work_dir
                        else Path(Path.home(), 'SI-DB-DATA'))
        the_db_file = Path(the_work_dir, the_db_name)
        print(
            f'2. @Base onInit\n\tDBN="{the_db_name}",'
            f'\n\tWDIR = "{the_work_dir}",'
            f'\n\tDBFP = "{the_db_file}"')

        self.__last_rows_affected__ = 0
        self.stack_ops_state = list()
        self.stack_select = list()
        self.db_suffix = '_DBF'
        print_if(f'The Suffix Test: {self.db_suffix}')
        self.db_path = os.path.expanduser(the_work_dir)
        self.db_file = os.path.expanduser(
                        f'{the_db_name}{self.db_suffix}.db'
                        if not the_db_name.endswith('.db')
                        else the_db_name)
        print_if(f'DB_File = [=- {self.db_file} -=]')
        temp_db_file = os.path.expanduser(Path(self.db_path, self.db_file))
        print_if(f'Temp DB File = [{temp_db_file}]')
        if not os.path.isdir(self.db_path):
            os.makedirs(self.db_path)
        if (not must_create_db) or (os.path.isdir(self.db_path) and not os.path.isfile(temp_db_file)):
            self.db_name = temp_db_file
        elif must_create_db or (os.path.isdir(self.db_path) and os.path.isfile(temp_db_file)):
            self.db_name = os.path.expanduser(os.path.\
                join(self.db_path,
                     f'{self.db_file[0:-3]}-on-' +
                     f'{datetime.now().strftime("%Y-%m-%d-@-%Ih-%Mm-%Ss-%fms-%p")}.db'))
        self.db_working_dir = self.database_path = os.path.expanduser(self.db_path if self.db_path else os.path.dirname(self.db_name))
        self.db_connection = None
    # ------------------------------------------------------------------------|

    def init_database(self, db_name=None, db_working_dir=None):
        """ Initializes database
        """
        self.db_working_dir =os.path.expanduser( db_working_dir if not (db_working_dir is None) \
            else Path(Path.home(), 'SI-Topics-DBs'))
        self.db_name = os.path.expanduser(db_name if not (db_name is None) \
            else 'SI_Topics_DB.db')
        self.db_name = os.path.expanduser(self.db_name \
            if self.db_name.endswith('.db') \
            else self.db_name + '.db')
        self.db_file = os.path.expanduser(Path(self.db_working_dir, self.db_name))

    # ------------------------------------------------------------------------|

    def __execute__(self, command: str, values: tuple = None):
        """ Convergence method for all executes without return
        """
        last_id = None
        db = None
        print_if(
            f'!!!! Running Execute for {command} with {values} for DB={self.db_name}')
        try:
            print_if(f'\n\tDbName = {self.db_name}\n\tType= {type(self.db_name)}')
            with sql.connect(str(self.db_name)) as db:
                print_if('1. Opened DB')
                cur = db.cursor()
                if values:
                    print_if('2a. Run command from Tuple')
                    last_id = cur.execute(command, values).lastrowid
                else:
                    print_if('2b. Run command NO-Tuple-Data')
                    last_id = cur.execute(command).lastrowid
                print_if('3. Count rows')
                rows = cur.rowcount
                print_if('4. Commit')
                db.commit()
                print_if('5. Update State')
                self.stack_ops_state.append(
                    ('OK.', f'Affected {rows} Row{"s" if rows>1 else ""}'))
        except sql.Error as sql_error:
            print_if(get_location(2))
            print_if(f'\nSQLite3 error: {sql_error.args}')
            print_if(f'Exception class is: {sql_error.__class__}')
            print_if('SQLite traceback: ')
            error_type, error_value, error_trace_back = sys.exc_info()
            extra = traceback.format_exception(error_type, error_value, error_trace_back)
            print_if(sql_error)
            print_if(extra)
        except Exception as ex:
            print_if(get_location(2))
            print_if(f'6. Failed as : {ex}')
            error_type, error_value, error_trace_back = sys.exc_info()
            extra = traceback.format_exception(error_type, error_value, error_trace_back)
            print_if(extra)            
            self.stack_ops_state.append(
                (f'\nFailed!\n', f'\tCommand Was:\n\t{command}', ex))
            if db:
                db.rollback()
        finally:
            if db:
                print_if('6. Closing DB')
                db.close()
        return last_id
    # ------------------------------------------------------------------------|

    def __select__(self, command: str, values: tuple) -> list:
        """ Convergence method for all queries execution without return (Update/Insert)
        """
        db = None
        records = list()
        try:
            with sql.connect(str(self.db_name)) as db:
                cur = db.cursor()
                cur.execute(command, values)
                bits = cur.fetchall()
                rows = cur.rowcount
                keys = cur.keys()
                self.stack_select.append(keys)
                for row in rows:
                    records.append(row)
                # db.commit()
                self.__last_rows_affected__ = rows
                self.stack_ops_state.append(
                    ('OK.', f'Affected {rows} Row{"s" if rows>1 else ""}'))
        except Exception as ex:
            self.stack_ops_state.append(
                (f'Failed!\n\t{ex}', f'\tCommand Was:\n\t{command}', ex))
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
            return records
    # ------------------------------------------------------------------------|

    def __select_array__(self, select_query: str, where_values: list):
        """ Generic select Query of multiple value tuples
            !!! the values parameter has to come in as a list of tuples !!!
        """
        # "insert into student (name, age, marks) values(?, ?, ?), (?, ?, ?),... (?, ?, ?);"
        self.__select__(select_query, tuple(where_values))
    # ------------------------------------------------------------------------|

    def __select_scalar__(self, command: str, values: tuple = None) -> int:
        """ Reusable internal method for all queries returning scalar
            e.g. select Max, Min, Count, etc
        """
        db = None
        scalar = -1
        try:
            with sql.connect(str(self.db_name)) as db:
                sql_cur = db.cursor()
                if values:
                    sql_cur.execute(command, values)
                else:
                    sql_cur.execute(command)
                # Bring the result into mem-space
                tuple_or_none = sql_cur.fetchone()   # sql_cur.fetchall()
                #print(f'Inside Select-Scalar: Returned : {tuple_or_None} \n\t\t Hash = {values}\n\t\t {command}')
                if not tuple_or_none is None:
                    # !!! Do not touch the comma below
                    # It is tuple transcending
                    (scalar,) = tuple_or_none
                db.commit()
                self.__last_rows_affected__ = 1
                self.stack_ops_state.append('Select Scalar OK.')
        except Exception as ex:
            print_if(get_location())
            self.stack_ops_state.append(
                (f'Failed!\n', f'\tCommand Was:\n\t{command}', ex))
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
        return scalar
    # ------------------------------------------------------------------------|

    def create_new_db(self, db_path: str = None) -> str:
        """ Creates a new database file
        """
        connection = None
        db_name = self.db_name
        print(db_name)
        try:
            connection = sql.connect(str(db_name))
            print_if(sql.version)
        except Exception as ex:
            print_if(get_location())
            print_if(ex)
        finally:
            if connection:
                connection.close()
    # ------------------------------------------------------------------------|

    def __insert_many__(self, insert_query: str, values: list):
        """ Generic insert Query of multiple value tuples
            !!! the values parameter has to come in as a list of tuples !!!
        """
        # "insert into student (name, age, marks) values(?, ?, ?), (?, ?, ?),... (?, ?, ?);"
        db = None
        try:
            with sql.connect(str(self.db_name)) as db:
                cur = db.cursor()
                cur.executemany(insert_query, values)
                db.commit()
            self.stack_ops_state.append("OK.")
        except Exception as ex:
            print_if(get_location())
            self.stack_ops_state.append(
                (f'Failed!\n\t{ex}', f'\tCommand Was:\n\t{insert_query}'
                 f'\tWith Params:\n\t{values}', ex))
            db.rollback()
        finally:
            db.close()
    # ------------------------------------------------------------------------|

    def __insert__(self, insert_query: str, values: tuple):
        """ Generic insert Query
        """
        # "insert into Teams (name, short, trigraph) values(?, ?, ?);"
        return self.__execute__(insert_query, values)
    # ------------------------------------------------------------------------|

    def __update__(self, update_query: str, update_values: tuple, where_values: tuple):
        """ Generic update Query of multiple value tuples
            !!! the values parameter has to come in as a list of tuples !!!
        """
        # "UPDATE teams set name = ?, short = ?, trigraphs = ? where id=?;"
        # for more rigor one can check the spaceholders count and sizes of tuples
        self.__execute__(update_query, update_values + where_values)
    # ------------------------------------------------------------------------|

    def is_table_in_db(self, table_name:str) -> bool:
        command = "SELECT Count(name) FROM sqlite_master WHERE type='table' AND name=?;"
        found_count = self.__select_scalar__(command, (table_name,))
        return found_count>0
    # ------------------------------------------------------------------------|

    def prepare_insert_statement(self, table_name: str, values: tuple,
                                 fields: list, debug_print: bool = True) -> str:
        """ Helpre method to prepare insert statement

        Args:
            table_name (str): INSERT statement's table nemae
            values (tuple): TUPLE containing the values for insertion
            fields (list): TABLE FIELDS to map to the inserted values to
            debug_print (bool, optional): Flog to print or ignore debug information. [Defaults to True.]

        Returns:
            str: The string of the actual COMMAND-TEXT capable of INSERT exacution
        """
        cmd = ""
        if table_name and fields and values and len(fields) == len(values):
            fields_list = ''.join([f'{str(e)},' for e in fields])
            values_list = ''.join(['?,' for e in values])
            cmd = (f' INSERT INTO {table_name}' +
                   f' ({fields_list[0:-1]})' +
                   f' VALUES ({values_list[0:-1]})'
                   )
        elif table_name and values and not fields:
            values_list = ''.join(['?,' for e in values])
            cmd = (f' INSERT INTO {table_name}' +
                   f' VALUES ({values_list[0:-1]})'
                   )
        else:
            # !!! TODO Fail Spectacularly !!!
            pass
        # Debugging the statement generation
        if debug_print:
            print_if(cmd)
        return cmd
    # ------------------------------------------------------------------------|

    def insert_row_to_table(self, table_name: str, values: tuple, fields: list = None):
        """ the publicly usable insert of the values into the table in a standart form
        @fields list is optional
        """
        cmd = self.prepare_insert_statement(table_name, values, fields)
        if cmd:
            print_if(f'Running:\n\t{cmd}\nwith values\n\t[{values}]')
            return self.__insert__(cmd, values)
        else:
            # !!! TODO Fail Spectacularly !!!
            return None
    # ------------------------------------------------------------------------|

    def pop_last_status(self, kill_all: bool = False) -> tuple:
        """Pops and (optionally) clears the last operation status
        """
        x = self.stack_ops_state.pop(-1)  # Pop the last entry
        if kill_all:
            self.stack_ops_state.clear()
        return x
    # ------------------------------------------------------------------------|

    def pop_select(self, kill_all: bool = False):
        """Pops and (optionally) clears the last select results
        """
        ret_value = self.stack_select.pop(-1)
        if kill_all:
            self.stack_select.clear()
        return ret_value
    # ------------------------------------------------------------------------|

    def print_stack(self, the_stack: list) -> int:
        """ Prints the error log--stack
        Args:
            the_stack (list): The log-stack
        Returns:
            (int): The length of the pronted stack
        """
        for (index, entry) in enumerate(the_stack):
            print_if(f'{index+1}.\tEntry:')
            for (j, sub) in enumerate(entry):
                if j == 0:
                    print_if(f'\t{j+1}.\tState:\t{sub}')
                if j == 1:
                    print_if(f'\t{j+1}.\tMessage:\t{sub}')
                if j > 1:
                    print_if(f'\t{j+1}.\Extra:\t{sub}')
        return len(the_stack)
    # ------------------------------------------------------------------------|
# ============================================================================||


if __name__ == "__main__":
    #test_table = True
    #if test_table:
       
    pass