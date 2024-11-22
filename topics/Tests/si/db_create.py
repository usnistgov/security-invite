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

import os
import sqlite3 as sql

import yaml
import db_base as dbBase
import argparse
import cred_crypto as pop


# user_name = 'dummy-1'
# password = '\' OR 1=1'
# cmd_sql_inject = (f"""
#        SELECT * from USERS 
#        WHERE user_name='{user_name}' and password_text='{password}'
#         """)

# ============================================================================||

class DbMaker(dbBase.BaseDB):
    """ Generic class for ToolChain sqlite handling
    Args:
        BaseDB ([type]): Extends a generic SQLite functionality from BaseDB
    """
    # ------------------------------------------------------------------------|

    def __init__(self,
                 db_path : str = '',
                 db_name: str = '',
                 must_create_db: bool = False
                 ):
        """ work_dir - Dir for the database file
            db_name - DB-file name
        """
        super().__init__(db_path, db_name, must_create_db=must_create_db)
        self.create_schema_if_needed()
        self.table_suffix = self.db_suffix[1:]  # Make sure to drop the dash
    # ------------------------------------------------------------------------|

    def create_db_file(self, close_after_created: bool = True):
        """ Creates the database SqLite-file and closes database after creation
            by default. Also checks to make sure that path-file does not exist yet
        """
        file_exists = os.path.isfile(self.db_file)
        if not file_exists:
            os.makedirs(self.database_path)
        self.db_connection = None
        try:
            dbBase.print_if(f"Connecting to file : {self.db_file}")
            self.db_connection = sql.connect(self.db_file)
        except Exception as general_exception:
            dbBase.print_if(general_exception)
        finally:
            if self.db_connection and close_after_created:
                self.db_connection.close()
    # ------------------------------------------------------------------------|

    def create_schema_if_needed(self):
        """ If database does not yet exist at the db_file path
            then create schema
        """
        if not os.path.isfile(self.db_file):
            dbBase.print_if(f'Creating Database at {self.db_file}')
            self.create_db_schema()
        else:
            dbBase.print_if(f'Using Existing Database at {self.db_file}')

    # ------------------------------------------------------------------------|
    def create_db_schema(self):
        """ Creates basic DB schema  with
            1. Admin Data:
                Teams<|--o>>Submissions
            2. Config+Test+Submission => Results Data:
                [Results] <<-- [Submissions [Admin Data]]
                [Configurations<|-- ; Tests<|-- ;] ->> [Results]
            3. Score Data:
                [Results]<|---0>[Scores]<<|--|>[ScoreTypes]<|--|>>[ScoreParams]
        """
        if not os.path.isfile(self.db_name):
            self.create_new_db()
        create_preamble = "CREATE TABLE IF NOT EXISTS "
        self.__execute__(f""" {create_preamble} 
                            "Users_Top50" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "user_name"	TEXT NOT NULL UNIQUE,
                            "password_text"	TEXT NOT NULL,
                            "failed_count"	INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY("id" AUTOINCREMENT));"""
                         )          
        self.__execute__(f""" {create_preamble} 
                            "Users_Top50H" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "user_name"	TEXT NOT NULL UNIQUE,
                            "salt"	TEXT NOT NULL,
                            "password_hash"	TEXT NOT NULL,
                            "failed_count"	INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY("id" AUTOINCREMENT));"""
                         )  
        self.__execute__(f""" {create_preamble} 
                            "Users_Top100" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "user_name"	TEXT NOT NULL UNIQUE,
                            "password_text"	TEXT NOT NULL,
                            "failed_count"	INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY("id" AUTOINCREMENT));"""
                         )   
        self.__execute__(f""" {create_preamble} 
                            "Users_Top100H" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "user_name"	TEXT NOT NULL UNIQUE,
                            "salt"	TEXT NOT NULL,
                            "password_hash"	TEXT NOT NULL,
                            "failed_count"	INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY("id" AUTOINCREMENT));"""
                         )   
        self.__execute__(f""" {create_preamble} 
                            "Users_Top500" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "user_name"	TEXT NOT NULL UNIQUE,
                            "password_text"	TEXT NOT NULL,
                            "failed_count"	INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY("id" AUTOINCREMENT));"""
                         )
        self.__execute__(f""" {create_preamble} 
                            "Users_Top500H" (
                            "id"	INTEGER NOT NULL UNIQUE,
                            "user_name"	TEXT NOT NULL UNIQUE,
                            "salt"	TEXT NOT NULL,
                            "password_hash"	TEXT NOT NULL,
                            "failed_count"	INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY("id" AUTOINCREMENT));"""
                         )
        self.__execute__(f""" {create_preamble} 
                         "Super_Duper_Secrets" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "account"	TEXT NOT NULL,
                                "account_pin"	TEXT NOT NULL,
                                "account_money"	TEXT NOT NULL,
                                "private_information"	TEXT NOT NULL,
                                PRIMARY KEY("id" AUTOINCREMENT));"""
                        )
        self.__execute__(f""" {create_preamble} 
                         "Top_Secrets" (
                                "id"	INTEGER NOT NULL UNIQUE,
                                "accounts"	TEXT NOT NULL,
                                "account_pins"	TEXT NOT NULL,
                                "account_money"	TEXT NOT NULL,
                                "private_information"	TEXT NOT NULL,
                                PRIMARY KEY("id" AUTOINCREMENT));"""
                        )
    # ------------------------------------------------------------------------|
    def populate_db_schema_hash(self, pwd_file_in: str, table_name:str ):
        """ Populates DB-File with password HASH and SALTS
        Args:
            pwd_file_in (str): THe data from the bad-passwords file
            table_name (str): the DB Table for filling in data
        """
        value_lines=[]
        file_lines=[]
        pwd_file = os.path.expanduser(pwd_file_in)
        if os.path.isfile(pwd_file):
            # read file lines
            with open(pwd_file) as file:
                file_lines = file.readlines()
            # loop over strings read from file
            for index, line in enumerate(file_lines, start=1):
                password = line.strip()
                ops = pop.PasswordOperations('sha512', 100_000)
                pass_hash, salt = ops.hash_new_password(password)
                value_lines.append(f"('dummy{index}', '{pass_hash}', '{salt}')")
            values = "\n\t, ".join(value_lines)
            insert =( f"INSERT INTO {table_name} ( user_name, password_hash, salt ) VALUES \n\t {values}")
            # print(f'\n\n\n\t{insert}')
            self.__insert__(insert, None)    
        else:
            print(f'The File [{pwd_file}] could not be found or is corrupted!')
    # ------------------------------------------------------------------------|
    def populate_from_map_hash(self, map_file):
        map_table_file = {}
        if os.path.isfile(map_file):    
            with open(map_file, "r") as stream:
                try:
                    map_table_file = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(f'\n\nyaml.YAMLError:\n{exc}\n\n')
                    status = -1
                except Exception as general_ex:
                    print(f'\n\nGeneral Exception:\n{general_ex}\n\n')
                    status = -10
                finally:
                    if stream:
                        stream.close()
            for table, pwd_file in map_table_file.items():
                self.populate_db_schema_hash( os.path.expanduser(pwd_file), table_name=f'{table}H')
        else:
            print(f'The File [{map_file}] could not be found or is corrupted!')
    # ------------------------------------------------------------------------|
    def populate_db_schema_simple(self, pwd_file_in: str, table_name:str ):
        """ Populates DB-File with 

        Args:
            pwd_file_in (str): _description_
            table_name (str): _description_
        """
        value_lines=[]
        file_lines=[]
        pwd_file = os.path.expanduser(pwd_file_in)
        if os.path.isfile(pwd_file):
            with open(pwd_file) as file:
                file_lines = file.readlines()
            for index, line in enumerate(file_lines, start=1):
                value_lines.append(f"('dummy{index}', '{line.strip()}')")
            values = "\n\t, ".join(value_lines)
            insert =( f"INSERT INTO {table_name} ( user_name, password_text ) VALUES \n\t {values}")
            # print(f'\n\n\n\t{insert}')
            self.__insert__(insert, None)    
        else:
            print(f'The File [{pwd_file}] could not be found or is corrupted!')
    # ------------------------------------------------------------------------|
    def populate_from_map_text(self, map_file):
        map_table_file = {}
        if os.path.isfile(map_file):    
            with open(map_file, "r") as stream:
                try:
                    map_table_file = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(f'\n\nyaml.YAMLError:\n{exc}\n\n')
                    status = -1
                except Exception as general_ex:
                    print(f'\n\nGeneral Exception:\n{general_ex}\n\n')
                    status = -10
                finally:
                    if stream:
                        stream.close()
            for table, pwd_file in map_table_file.items():
                self.populate_db_schema_simple( os.path.expanduser(pwd_file), table_name=table)
        else:
            print(f'The File [{map_file}] could not be found or is corrupted!')
    # ------------------------------------------------------------------------|
# ============================================================================||

def parse_args(default_wd: str, default_db: str, default_map_file:str ) -> tuple:
    parser = argparse.ArgumentParser(
        prog = 'python3 db_create.py',
        description = """
        NIST Security InVITE DB Creation-Initialization Python Script [in File db_create.py]        
        InVITE stands for [In]tro to [V]irtualized [I]ntegrated [T]esting&Teaching [E]nvironment)

        The script allows easier creation/initialization of the fake credentials SQLite3 database
        filled in with the passwords sourced from the Top 50/100/500/1,000/10,000 subset of the 
        wikipedia listed most popular passwords:
        https://en.wikipedia.org/wiki/Wikipedia:10,000_most_common_passwords""",
        epilog='WARNING: Do not ever use any of these passwords if you expect to maintain your security posture!'
    )
    # Adding optional argument
    parser.add_argument("-wd", "--WorkDir", 
                        help = "Directory inside of which to Create DB File [Default ~/]",
                        default = default_wd
                        ) 
    parser.add_argument("-db", "--Database", 
                        help = "Database file name [Default SI_DB.db]",
                        default = default_db
                        ) 
    
    parser.add_argument("-pm", "--PassMap", 
                        help = "YAML file with BAD PASSWORD FILE mapped to populate-enumerate tables",
                        default = default_map_file
                        ) 
    args = parser.parse_args()
    print(args.WorkDir, args.Database, args.PassMap)
    return  (args.WorkDir, args.Database, args.PassMap)

if __name__ == "__main__":
     # Initialize parser
    default_wd = '~/si/db'
    default_db = 'SI_DBF.db'    
    path, db, map_file = parse_args(default_wd, default_db,  '~/si/map_ubu.yaml')

    if path and db: # should be 100% now, but still the elses are already written from before :)
        db_maker = DbMaker(db_path =path, db_name=db)
    elif not path and db:
        db_maker = DbMaker(db_path =default_wd, db_name=db)
    elif path and not db:
        db_maker = DbMaker(db_path =path, db_name=default_db)
    else:
        db_maker = DbMaker(db_path =default_wd, db_name=default_db)

    db_maker.create_db_schema()
    db_maker.populate_from_map_text(map_file)
    db_maker.populate_from_map_hash(map_file)